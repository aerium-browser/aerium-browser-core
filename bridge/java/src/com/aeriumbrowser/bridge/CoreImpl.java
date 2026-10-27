// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.bridge;

import com.aeriumbrowser.api.ActionsApi;
import com.aeriumbrowser.api.AeriumCore;
import com.aeriumbrowser.api.BrowsingDataApi;
import com.aeriumbrowser.api.ExtensionsApi;
import com.aeriumbrowser.api.NavigationApi;
import com.aeriumbrowser.api.PrefsApi;
import com.aeriumbrowser.api.SettingsApi;
import com.aeriumbrowser.api.SitesApi;
import com.aeriumbrowser.api.TabsApi;
import com.aeriumbrowser.api.WebAppsApi;

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
