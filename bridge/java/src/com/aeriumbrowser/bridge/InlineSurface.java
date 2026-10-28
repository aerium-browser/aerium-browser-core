// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.bridge;

import android.content.Context;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.Nullable;

import com.aeriumbrowser.api.AeriumCore;
import com.aeriumbrowser.api.Slot;
import com.aeriumbrowser.api.SurfaceFactory;
import com.aeriumbrowser.api.SurfaceHost;

import org.chromium.chrome.browser.tab.Tab;

public final class InlineSurface implements SurfaceHost {
    private final Context mContext;
    private final int mTabId;
    private @Nullable View mView;

    private InlineSurface(Context context, int tabId) {
        mContext = context;
        mTabId = tabId;
    }

    public static void insertBefore(@Nullable View anchor, Tab tab, Slot slot) {
        if (anchor == null || !(anchor.getParent() instanceof ViewGroup parent)) return;
        SurfaceFactory factory = AeriumUi.surface(slot);
        if (factory == null) return;
        InlineSurface host = new InlineSurface(anchor.getContext(), tab.getId());
        View view = factory.create(anchor.getContext(), host);
        if (view == null) return;
        host.mView = view;
        parent.addView(
                view,
                parent.indexOfChild(anchor),
                new ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
    }

    @Override
    public AeriumCore core() {
        return Aerium.core();
    }

    @Override
    public int tabId() {
        return mTabId;
    }

    @Override
    public void close() {
        View view = mView;
        mView = null;
        if (view != null && view.getParent() instanceof ViewGroup parent) parent.removeView(view);
    }

    @Override
    public void open(Slot slot) {
        SurfaceFragment.start(mContext, slot);
    }

    @Override
    public void showDefault() {}
}
