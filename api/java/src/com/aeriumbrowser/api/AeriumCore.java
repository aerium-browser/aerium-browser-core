// Copyright 2026 Dioide
// SPDX-License-Identifier: GPL-3.0-only

package com.aeriumbrowser.api;

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
