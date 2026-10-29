// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.bridge;

import com.aeriumbrowser.android.api.ActionsApi;
import com.aeriumbrowser.android.api.AeriumCore;
import com.aeriumbrowser.android.api.BrowsingDataApi;
import com.aeriumbrowser.android.api.ExtensionsApi;
import com.aeriumbrowser.android.api.NavigationApi;
import com.aeriumbrowser.android.api.PrefsApi;
import com.aeriumbrowser.android.api.SettingsApi;
import com.aeriumbrowser.android.api.SitesApi;
import com.aeriumbrowser.android.api.TabsApi;
import com.aeriumbrowser.android.api.WebAppsApi;

final class CoreImpl implements AeriumCore {
    private final SettingsApi mSettings = new SettingsImpl();
    private final TabsApi mTabs = new TabsImpl();
    private final NavigationApi mNavigation = new NavigationImpl();
    private final BrowsingDataApi mBrowsingData = new BrowsingDataImpl();
    private final ExtensionsApi mExtensions = new ExtensionsImpl();
    private final SitesApi mSites = new SitesImpl();
    private final PrefsApi mPrefs = new PrefsImpl();
    private final ActionsApi mActions = new ActionsImpl();
    private final WebAppsApi mWebApps = new WebAppsImpl();

    @Override
    public int apiVersion() {
        return VERSION;
    }

    @Override
    public SettingsApi settings() {
        return mSettings;
    }

    @Override
    public TabsApi tabs() {
        return mTabs;
    }

    @Override
    public NavigationApi navigation() {
        return mNavigation;
    }

    @Override
    public BrowsingDataApi browsingData() {
        return mBrowsingData;
    }

    @Override
    public ExtensionsApi extensions() {
        return mExtensions;
    }

    @Override
    public SitesApi sites() {
        return mSites;
    }

    @Override
    public PrefsApi prefs() {
        return mPrefs;
    }

    @Override
    public ActionsApi actions() {
        return mActions;
    }

    @Override
    public WebAppsApi webApps() {
        return mWebApps;
    }
}
