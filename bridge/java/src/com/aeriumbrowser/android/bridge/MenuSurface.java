// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.bridge;

import android.app.Activity;
import android.content.Context;
import android.view.View;

import androidx.annotation.Nullable;

import com.aeriumbrowser.android.api.MenuHost;
import com.aeriumbrowser.android.api.MenuItem;
import com.aeriumbrowser.android.api.Slot;
import com.aeriumbrowser.android.api.SurfaceFactory;

import org.chromium.base.ContextUtils;
import org.chromium.chrome.browser.app.ChromeActivity;
import org.chromium.chrome.browser.tab.Tab;
import org.chromium.chrome.browser.ui.appmenu.AppMenuItemProperties;
import org.chromium.chrome.browser.ui.appmenu.AppMenuItemWithSubmenuProperties;
import org.chromium.chrome.browser.ui.appmenu.AppMenuSheet;
import org.chromium.ui.modelutil.MVCListAdapter.ListItem;
import org.chromium.ui.modelutil.MVCListAdapter.ModelList;
import org.chromium.ui.modelutil.PropertyModel;

import java.lang.ref.WeakReference;
import java.util.List;
import java.util.function.Supplier;

public final class MenuSurface implements AppMenuSheet.Presenter {
    private static @Nullable WeakReference<ModelList> sPageMenu;
    private static @Nullable WeakReference<ModelList> sOverviewMenu;

    private MenuSurface() {}

    public static void attach(ModelList menu, boolean overview) {
        WeakReference<ModelList> ref = new WeakReference<>(menu);
        if (overview) {
            sOverviewMenu = ref;
        } else {
            sPageMenu = ref;
        }
        if (AppMenuSheet.getPresenter() == null) AppMenuSheet.setPresenter(new MenuSurface());
    }

    private static boolean holds(@Nullable WeakReference<ModelList> ref, ModelList items) {
        return ref != null && ref.get() == items;
    }

    @Override
    public @Nullable AppMenuSheet.Session show(
            Context context, ModelList items, AppMenuSheet.Host host) {
        boolean overview = holds(sOverviewMenu, items);
        if (!overview && !holds(sPageMenu, items)) return null;
        SurfaceFactory factory = AeriumUi.surface(Slot.MENU);
        Activity activity = ContextUtils.activityFromContext(context);
        if (factory == null || activity == null || activity.isFinishing()) return null;
        Tab tab = activity instanceof ChromeActivity chrome ? chrome.getActivityTab() : null;
        Sheet sheet =
                new Sheet(
                        activity,
                        tab == null ? MenuHost.NO_TAB : tab.getId(),
                        items,
                        host,
                        overview);
        View view = factory.create(activity, sheet);
        if (view == null) return null;
        sheet.dialog().setOnDismissListener(dialog -> host.dismissed());
        sheet.present(view, SurfaceDialog.isNight(activity), false);
        return sheet;
    }

    private static @Nullable PropertyModel find(ModelList list, int id) {
        for (int i = 0; i < list.size(); i++) {
            PropertyModel inner = findIn(list.get(i).model, id);
            if (inner != null) return inner;
        }
        return null;
    }

    private static @Nullable PropertyModel findIn(PropertyModel model, int id) {
        if (model.containsKey(AppMenuItemProperties.MENU_ITEM_ID)
                && model.get(AppMenuItemProperties.MENU_ITEM_ID) == id) {
            return model;
        }
        if (model.containsKey(AppMenuItemProperties.ADDITIONAL_ICONS)) {
            ModelList icons = model.get(AppMenuItemProperties.ADDITIONAL_ICONS);
            if (icons != null) {
                PropertyModel inner = find(icons, id);
                if (inner != null) return inner;
            }
        }
        if (model.containsKey(AppMenuItemWithSubmenuProperties.SUBMENU_PROVIDER)) {
            Supplier<List<ListItem>> submenu =
                    model.get(AppMenuItemWithSubmenuProperties.SUBMENU_PROVIDER);
            List<ListItem> children = submenu == null ? null : submenu.get();
            if (children != null) {
                for (ListItem child : children) {
                    PropertyModel inner = findIn(child.model, id);
                    if (inner != null) return inner;
                }
            }
        }
        return null;
    }

    private static boolean has(PropertyModel model, PropertyModel.WritableBooleanPropertyKey key) {
        if (model.containsKey(key) && model.get(key)) return true;
        if (!model.containsKey(AppMenuItemProperties.ADDITIONAL_ICONS)) return false;
        ModelList icons = model.get(AppMenuItemProperties.ADDITIONAL_ICONS);
        if (icons == null) return false;
        for (int i = 0; i < icons.size(); i++) {
            PropertyModel inner = icons.get(i).model;
            if (inner.containsKey(key) && inner.get(key)) return true;
        }
        return false;
    }

    private static final class Sheet extends SurfaceDialog
            implements MenuHost, AppMenuSheet.Session {
        private final ModelList mItems;
        private final AppMenuSheet.Host mHost;
        private final boolean mOverview;

        Sheet(
                Activity activity,
                int tabId,
                ModelList items,
                AppMenuSheet.Host host,
                boolean overview) {
            super(activity, tabId, () -> {});
            mItems = items;
            mHost = host;
            mOverview = overview;
        }

        @Override
        public boolean overview() {
            return mOverview;
        }

        @Override
        public @Nullable MenuItem item(int id) {
            PropertyModel model = find(mItems, id);
            if (model == null) return null;
            boolean enabled =
                    !model.containsKey(AppMenuItemProperties.ENABLED)
                            || model.get(AppMenuItemProperties.ENABLED);
            return new MenuItem(
                    id,
                    enabled,
                    has(model, AppMenuItemProperties.CHECKABLE),
                    has(model, AppMenuItemProperties.CHECKED));
        }

        @Override
        public void select(int id) {
            close();
            mHost.select(id);
        }

        @Override
        public boolean isShowing() {
            return dialog().isShowing();
        }

        @Override
        public void dismiss() {
            close();
        }
    }
}
