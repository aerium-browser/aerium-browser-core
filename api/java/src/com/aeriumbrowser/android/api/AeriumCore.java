// Copyright 2026 Aerium Browser
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.android.api;

public interface AeriumCore {
    int VERSION = 1;

    int apiVersion();

    SettingsApi settings();

    TabsApi tabs();

    NavigationApi navigation();

    BrowsingDataApi browsingData();

    ExtensionsApi extensions();

    SitesApi sites();

    PrefsApi prefs();

    ActionsApi actions();

    WebAppsApi webApps();
}
