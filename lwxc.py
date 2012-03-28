#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2012 Thomas Krug
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re
import signal
import subprocess
import sys
import configparser
import optparse

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib

import xmmsclient
import xmmsclient.collections

class window_main():

    window = None
    pos_x = -1
    pos_y = -1
    artists = None
    artists_sel = None
    albums = None
    albums_sel = None
    tracks = None
    tracks_sel = None
    playlists = None
    playlists_sel = None
    playlists_tv = None
    playlists_sw = None
    playlist = None
    playlist_tv = None
    playlist_sw = None

    playlist_changing = False

    artists_selection = []
    artists_selection_prev = []
    albums_selection = []
    albums_selection_prev = []
    tracks_selection = []
    tracks_selection_prev = []

    dialog = None
    dialog_entry = None

    coll_artists = None
    coll_albums = None
    coll_tracks = None

    def __init__(self, instance):

        self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
        self.window.connect("delete-event", self.on_delete_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        self.window.connect("configure-event", self.on_configure_event)
        self.window.connect("key-press-event", self.on_key_press_event)
        self.window.set_title("le wild xmms2 client")
        self.window.set_icon_from_file(iconname)
        self.window.set_wmclass(instance, "LWXC")
        screen = self.window.get_screen()
        width = screen.get_width() * 0.75
        height = screen.get_height() * 0.75
        self.window.set_size_request(int(width), int(height))
        self.window.set_position(Gtk.WindowPosition.CENTER)

        if config.get_maximize():
            self.window.maximize()

        if config.get_skip_taskbar():
            self.window.set_skip_taskbar_hint(True)

        vbox1 = Gtk.VBox(False, 0)
        self.window.add(vbox1)

        hbox1 = Gtk.HBox(False, 0)
        vbox1.pack_start(hbox1, True, True, 0)

        artists_sw = Gtk.ScrolledWindow()
        artists_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox1.pack_start(artists_sw, True, True, 0)


        artists_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Artists", cel, text=0)
        artists_tv.append_column(col)
        artists_tv.set_headers_visible(False)

        self.artists_sel = artists_tv.get_selection()
        self.artists_sel.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.artists_sel.connect("changed", self.on_artists_selection_changed)

        self.artists = Gtk.ListStore(str)
        artists_tv.set_model(self.artists)

        artists_tv.connect("row-activated", self.on_artists_activated)

        artists_sw.add(artists_tv)

        connection.get_artists(self.artists)


        vsep1 = Gtk.VSeparator()
        hbox1.pack_start(vsep1, False, False, 0)

        albums_sw = Gtk.ScrolledWindow()
        albums_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox1.pack_start(albums_sw, True, True, 0)


        albums_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Albums", cel, text=0)
        albums_tv.append_column(col)
        albums_tv.set_headers_visible(False)

        self.albums_sel = albums_tv.get_selection()
        self.albums_sel.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.albums_sel.connect("changed", self.on_albums_selection_changed)

        self.albums = Gtk.ListStore(str)
        albums_tv.set_model(self.albums)

        albums_tv.connect("row-activated", self.on_albums_activated)

        albums_sw.add(albums_tv)


        vsep2 = Gtk.VSeparator()
        hbox1.pack_start(vsep2, False, False, 0)

        tracks_sw = Gtk.ScrolledWindow()
        tracks_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox1.pack_start(tracks_sw, True, True, 0)


        tracks_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Tracks", cel, text=0)
        tracks_tv.append_column(col)
        tracks_tv.set_headers_visible(False)

        self.tracks_sel = tracks_tv.get_selection()
        self.tracks_sel.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.tracks_sel.connect("changed", self.on_tracks_selection_changed)

        self.tracks = Gtk.ListStore(str)
        tracks_tv.set_model(self.tracks)

        tracks_tv.connect("row-activated", self.on_tracks_activated)

        tracks_sw.add(tracks_tv)


        vsep3 = Gtk.VSeparator()
        hbox1.pack_start(vsep3, False, False, 0)

        vbox2 = Gtk.VBox(False, 0)
        hbox1.pack_end(vbox2, True, True, 0)

        self.playlists_sw = Gtk.ScrolledWindow()
        self.playlists_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox2.pack_start(self.playlists_sw, False, False, 0)


        self.playlists_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Playlists", cel, markup=0)
        self.playlists_tv.append_column(col)
        self.playlists_tv.set_headers_visible(False)

        self.playlists_sel = self.playlists_tv.get_selection()
        self.playlists_sel.set_mode(Gtk.SelectionMode.SINGLE)

        self.playlists = Gtk.ListStore(str)
        self.playlists_tv.set_model(self.playlists)

        self.playlists_tv.connect("row-activated", self.on_playlists_activated)
        self.playlists_tv.connect("button-press-event", self.on_playlists_button_press)
        self.playlists_tv.connect("popup-menu", self.on_playlists_popup_menu)

        self.playlists_sw.add(self.playlists_tv)

        connection.get_playlists()


        hsep1 = Gtk.HSeparator()
        vbox2.pack_start(hsep1, False, False, 0)

        self.playlist_sw = Gtk.ScrolledWindow()
        self.playlist_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        vbox2.pack_start(self.playlist_sw, True, True, 0)


        self.playlist_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Playlist", cel, markup=0)
        self.playlist_tv.append_column(col)
        self.playlist_tv.set_headers_visible(False)

        playlist_sel = self.playlist_tv.get_selection()
        playlist_sel.set_mode(Gtk.SelectionMode.SINGLE)

        self.playlist = Gtk.ListStore(str)
        self.playlist_tv.set_model(self.playlist)

        self.playlist_tv.connect("row-activated", self.on_playlist_activated)
        self.playlist_tv.connect("key-press-event", self.on_playlist_key_press)

        self.playlist_sw.add(self.playlist_tv)

        connection.get_playlist()


        # no seekbar at the moment
        #hbox2 = Gtk.HBox(False, 0)
        #vbox1.pack_start(hbox2, False, False, 0)

        #seekbar = Gtk.HScale()
        #hbox2.pack_start(seekbar, True, True, 0)
        #seekbar.set_draw_value(False)

        #volume = Gtk.VolumeButton()
        #hbox2.pack_start(volume, False, False, 0)


        vbox1.show_all()

        connection.setup_playlists_cb(self.on_playlists_changed)
        connection.setup_playlist_cb(self.on_playlist_changed)

    def quit(self, widget):
        loop.quit()

    def toggle(self, widget=None):
        if self.window.get_property("visible"):
            self.pos_x, self.pos_y = self.window.get_position()
            self.window.hide()
        else:
            self.window.deiconify()
            self.window.present()
            if self.pos_x != -1:
                screen = self.window.get_screen()
                pos_x = self.pos_x % screen.get_width()
                pos_y = self.pos_y % screen.get_height()
                self.window.move(pos_x, pos_y)

    def on_delete_event(self, widget, event):
        self.window.hide()
        return True

    def on_window_state_event(self, widget, event):
        if event.new_window_state & Gdk.WindowState.ICONIFIED:
            self.window.hide()

    def on_configure_event(self, widget, event):
        if not self.playlists_sw:
            return

        (width, height) = self.window.get_size()

        new_height = int(height / 100 * 15)

        self.playlists_sw.set_min_content_height(new_height)

    def on_key_press_event(self, window, event):

        if event.keyval == Gdk.KEY_Right:
            self.window.get_toplevel().child_focus(Gtk.DirectionType.TAB_FORWARD)

        if event.keyval == Gdk.KEY_Left:
            self.window.get_toplevel().child_focus(Gtk.DirectionType.TAB_BACKWARD)

    def on_artists_selection_changed(self, treeview):
        self.artists_selection_prev = self.artists_selection
        (model, pathlist) = self.artists_sel.get_selected_rows()
        self.artists_selection = pathlist

        artists = []
        for path in pathlist:
            iter = model.get_iter(path)
            artists.append(model.get_value(iter, 0))

        connection.get_albums(self.albums, artists)

    def on_albums_selection_changed(self, treeview):
        self.albums_selection_prev = self.albums_selection
        (model, pathlist) = self.albums_sel.get_selected_rows()
        self.albums_selection = pathlist

        albums = []
        for path in pathlist:
            iter = model.get_iter(path)
            albums.append(model.get_value(iter, 0))

        connection.get_tracks(self.tracks, albums)

    def on_tracks_selection_changed(self, treeview):
        self.tracks_selection_prev = self.tracks_selection
        (model, pathlist) = self.tracks_sel.get_selected_rows()
        self.tracks_selection = pathlist

    def on_artists_activated(self, treeview, iter, path):
        selection = treeview.get_selection()
        (model, pathlist) = selection.get_selected_rows()

        pathlist = self.artists_selection_prev

        artists = []
        for path in pathlist:
            iter = model.get_iter(path)
            artists.append(model.get_value(iter, 0))
            selection.select_path(path)

        connection.add_artists(artists)

    def on_albums_activated(self, treeview, iter, path):
        selection = treeview.get_selection()
        (model, pathlist) = selection.get_selected_rows()

        pathlist = self.albums_selection_prev

        albums = []
        for path in pathlist:
            iter = model.get_iter(path)
            albums.append(model.get_value(iter, 0))
            selection.select_path(path)

        connection.add_albums(albums)

    def on_tracks_activated(self, treeview, iter, path):
        selection = treeview.get_selection()
        (model, pathlist) = selection.get_selected_rows()

        pathlist = self.tracks_selection_prev

        tracks = []
        for path in pathlist:
            iter = model.get_iter(path)
            tracks.append(model.get_value(iter, 0))
            selection.select_path(path)

        connection.add_tracks(tracks)

    def on_playlists_activated(self, treeview, path, column):
        connection.load_playlist(get_selected_entry(treeview))

    def on_playlist_activated(self, treeview, path, column):
        connection.jump_to(get_selected_entry_position(treeview))

    def on_playlists_button_press(self, treeview, event):

        if event.button == 3:
            pthinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.set_cursor(path, col, 0)

            self.playlists_menu(treeview, event)

            return True

        return False

    def on_playlist_key_press(self, treeview, event):

        if event.keyval == Gdk.KEY_Delete:
            connection.remove_playlist_entry(get_selected_entry_position(treeview))

    def on_playlists_changed(self, result):
        connection.get_playlists()

    def on_playlist_changed(self, result):
        # meh
        if not connection.update:
            connection.get_playlist()

    def on_playlists_popup_menu(self, widget):
        self.playlists_menu(widget, None)
        return True

    def playlists_menu(self, treeview, event):

        # get selected playlist
        selection = treeview.get_selection()
        (model, it) = selection.get_selected()
        if it:
            playlist = model.get_value(it, 0)

        # build popup menu
        menu = Gtk.Menu()

        create = Gtk.MenuItem("new playlist")
        create.connect("activate", self.show_text_entry_dialog)
        menu.append(create)

        # add items if playlist selected
        if it:
            playlist = remove_pango(playlist)

            clear = Gtk.MenuItem("clear " + playlist)
            clear.connect("activate", connection.playlist_clear, playlist)
            menu.append(clear)

            remove = Gtk.MenuItem("remove " + playlist)
            remove.connect("activate", connection.playlist_remove, playlist)
            menu.append(remove)

        menu.show_all()
        menu.attach_to_widget(treeview, None)

        # right click
        if event:
            menu.popup(None, None, None, None, event.button, event.time)

        # menu key press
        else:
            path = model.get_path(it)
            cell_area = treeview.get_cell_area(path, treeview.get_column(0))
            foo, x, y = treeview.get_bin_window().get_origin()
            y += cell_area.y

            menu.popup(None, None, self.position_menu, (x, y), 0, 0)

    def position_menu(window, menu, data):
        (x, y) = data
        return (x, y, False)

    def show_about_dialog(self, widget):
        about_dialog = Gtk.AboutDialog()

        about_dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        about_dialog.set_transient_for(self.window)

        about_dialog.set_name("le wild xmms2 client")
        about_dialog.set_version("0.1")
        #about_dialog.set_comments("Ein einfacher Medien-Bibliothek Browser für XMMS2, mit Fokus auf Tastaturbedienbarkeit.")
        about_dialog.set_comments("A simple media library browser for XMMS2, with a focus on keyboard operability.")
        #about_dialog.set_authors(["Thomas Krug"])
        about_dialog.set_copyright("Copyright © 2012 Thomas Krug")
        about_dialog.set_website("http://phragment.github.com/lwxc/")
        about_dialog.set_website_label("phragment.github.com/lwxc")

        about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size(iconname, 200, 200))

        about_dialog.run()
        about_dialog.destroy()

    def show_text_entry_dialog(self, widget):
        self.dialog = Gtk.Dialog("new playlist", self.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.dialog.set_size_request(300, 80)

        label = Gtk.Label(label="Please enter name:")
        self.dialog.vbox.pack_start(label, True, True, 0)

        self.dialog_entry = Gtk.Entry()
        self.dialog_entry.connect("activate", self.on_input_dialog)
        self.dialog.vbox.pack_start(self.dialog_entry, False, False, 0)
        self.dialog.show_all()

        self.dialog.run()
        self.dialog.destroy()

    def on_input_dialog(self, widget):

        text = self.dialog_entry.get_text()
        self.dialog.destroy()

        # sanitize text
        #  remove leading underscores
        #  remove leading and trailing whitespaces
        text = text.lstrip("_").strip()

        if text is "":
            return

        connection.playlist_create(text)


def get_selected_entry(treeview):
    selection = treeview.get_selection()
    (model, treeiter) = selection.get_selected()
    if not treeiter:
        return ""
    value = model.get_value(treeiter, 0)
    return value

def get_selected_entry_position(treeview):
    selection = treeview.get_selection()
    (model, treeiter) = selection.get_selected()
    if not treeiter:
        return -1
    path = model.get_path(treeiter)
    index = path.get_indices()
    return index[0]


class TrayIcon():

    icon = None
    menu = None

    def __init__(self):
        self.icon = Gtk.StatusIcon()
        self.icon.set_from_file(iconname)
        self.icon.connect("activate", window.toggle)
        self.icon.connect("popup-menu", self.on_popup_menu)

        self.menu = Gtk.Menu()

        play = Gtk.MenuItem("Play")
        play.connect("activate", connection.play)
        self.menu.append(play)

        pause = Gtk.MenuItem("Pause")
        pause.connect("activate", connection.pause)
        self.menu.append(pause)

        stop = Gtk.MenuItem("Stop")
        stop.connect("activate", connection.stop)
        self.menu.append(stop)

        sep1 = Gtk.SeparatorMenuItem()
        self.menu.append(sep1)

        prev = Gtk.MenuItem("Prev")
        prev.connect("activate", connection.prev)
        self.menu.append(prev)

        next_ = Gtk.MenuItem("Next")
        next_.connect("activate", connection.next_)
        self.menu.append(next_)

        sep1 = Gtk.SeparatorMenuItem()
        self.menu.append(sep1)

        about = Gtk.MenuItem("About")
        about.connect("activate", window.show_about_dialog)
        self.menu.append(about)

        quit = Gtk.MenuItem("Quit")
        quit.connect("activate", self.quit)
        self.menu.append(quit)

    def quit(self, widget):
        loop.quit()

    def on_popup_menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, None, button, time)


"""
 A GLib connector for PyGTK - to use with your cool PyGTK xmms2 client.
 Tobias Rundstrom <tru@xmms.org>
 Raphaël Bois <virtualdust@gmail.com>

 rewritten to use with gi.repository.GObject
"""

class GLibConnector:
    def __init__(self, xmms):
        self.in_id = None
        self.out_id = None
        self.reconnect(xmms)

    def need_out(self, i):
        if self.xmms.want_ioout() and self.out_id is None:
            self.out_id = GObject.io_add_watch(self.xmms.get_fd(), GObject.IO_OUT, self.handle_out)

    def handle_in(self, source, cond):
        if cond == GObject.IO_IN:
            return self.xmms.ioin()

        return True

    def handle_out(self, source, cond):
        if cond == GObject.IO_OUT and self.xmms.want_ioout():
            self.xmms.ioout()
        if not self.xmms.want_ioout():
            self.out_id = None

        return not self.out_id is None

    def reconnect(self, xmms=None):
        self.disconnect()
        if not xmms is None:
            self.xmms = xmms
        self.xmms.set_need_out_fun(self.need_out)
        self.in_id = GObject.io_add_watch(self.xmms.get_fd(), GObject.IO_IN, self.handle_in)
        self.out_id = None

    def disconnect(self):
        if not self.in_id is None:
            GObject.source_remove(self.in_id)
            self.in_id = None
        if not self.out_id is None:
            GObject.source_remove(self.out_id)
            self.out_id = None

class Connection:

    xmms_async = None

    update = False

    def __init__(self):

        self.xmms_async = xmmsclient.XMMS("lwxc")

        try:
            self.xmms_async.connect(os.getenv("XMMS_PATH"), disconnect_func=self.disconnect)
        except IOError as detail:
            if config.get_autostart():
                subprocess.check_call("xmms2-launcher")
                # would like to use goto here
                self.xmms_async.connect(os.getenv("XMMS_PATH"), disconnect_func=self.disconnect)
            else:
                print("Error:", detail)
                sys.exit(1)

        conn = GLibConnector(self.xmms_async)

    def play(self, widget):
        self.xmms_async.playback_start()

    def pause(self, widget):
        self.xmms_async.playback_pause()

    def stop(self, widget):
        self.xmms_async.playback_stop()

    def next_(self, widget):
        self.xmms_async.playlist_set_next_rel(1)
        self.xmms_async.playback_tickle()

    def prev(self, widget):
        self.xmms_async.playlist_set_next_rel(-1)
        self.xmms_async.playback_tickle()


    def add_artists(self, artists):
        coll = xmmsclient.collections.IDList()
        for artist in artists:
            coll = coll | self.coll_artists & xmmsclient.collections.Match(field="artist", value=artist)

        self.xmms_async.playlist_add_collection(coll, ['artist', 'date', 'album', 'tracknr', 'title'])

    def add_albums(self, albums):
        coll = xmmsclient.collections.IDList()
        for album in albums:
            coll = coll | self.coll_albums & xmmsclient.collections.Match(field="album", value=album)

        self.xmms_async.playlist_add_collection(coll, ['artist', 'date', 'album', 'tracknr', 'title'])

    def add_tracks(self, tracks):
        coll = xmmsclient.collections.IDList()
        for track in tracks:
            coll = coll | self.coll_tracks & xmmsclient.collections.Match(field="title", value=track)

        self.xmms_async.playlist_add_collection(coll, ["artist", "date", "album", "tracknr", "title"])


    def get_artists(self, store):
        artists = xmmsclient.collections.Match(field="artist", value="*")
        self.coll_artists = artists

        fetch = {
            "type": "cluster-list",
            "cluster-by": "value",
            "cluster-field": "artist",
            "data": {
                "type": "metadata",
                "get": ["value"],
                "fields": ["artist"]
            }
        }

        def get_artists_done(result):
            if result.is_error():
                print(result.value())
            else:
                store.clear()
                for artist in result.value():
                    store.append([artist])

        self.xmms_async.coll_query(xmmsclient.collections.Order(artists, field="artist"), fetch, get_artists_done)

    def get_albums(self, store, artists):
        if not store:
            return

        albums = xmmsclient.collections.IDList()
        for artist in artists:
            albums = albums | self.coll_artists & xmmsclient.collections.Match(field="artist", value=artist)

        self.coll_albums = albums

        fetch = {
            "type": "cluster-list",
            "cluster-by": "value",
            "cluster-field": "album",
            "data": {
                "type": "metadata",
                "get": ["value"],
                "fields": ["album"]
            }
        }

        def get_albums_done(result):
            if result.is_error():
                print(result.value())
            else:
                store.clear()
                for album in result.value():
                    store.append([album])

        self.xmms_async.coll_query(xmmsclient.collections.Order(xmmsclient.collections.Order(xmmsclient.collections.Order(albums, field="album"), field="date"), field="artist"), fetch, get_albums_done)

    def get_tracks(self, store, albums):
        if not store:
            return

        tracks = xmmsclient.collections.IDList()
        for album in albums:
            tracks = tracks | self.coll_albums & xmmsclient.collections.Match(field="album", value=album)

        self.coll_tracks = tracks

        fetch = {
            "type": "cluster-list",
            "cluster-by": "value",
            "cluster-field": "title",
            "data": {
                "type": "metadata",
                "get": ["value"],
                "fields": ["title"]
            }
        }

        def get_tracks_done(result):
            if result.is_error():
                print(result.value())
            else:
                store.clear()
                for track in result.value():
                    store.append([track])

        self.xmms_async.coll_query(xmmsclient.collections.Order(xmmsclient.collections.Order(xmmsclient.collections.Order(xmmsclient.collections.Order(xmmsclient.collections.Order(tracks, field="title"), field="tracknr"), field="album"), field="date"), field="artist"), fetch, get_tracks_done)

    def load_playlist(self, name):
        self.xmms_async.playlist_load(name)

    def get_playlists(self):
        self.xmms_async.playlist_current_active(cb=self.got_current_playlist)

    def got_current_playlist(self, result):
        if result.is_error():
            print(result.value())
        else:
            self.current_playlist = result.value()
            self.xmms_async.playlist_list(cb=self.got_playlists)

    def got_playlists(self, result):
        store = window.playlists;
        view = window.playlists_tv;
        current = self.current_playlist
        selection = window.playlists_sel

        if result.is_error():
            print(result.value())
        else:
            playlists = result.value()

            # store selection
            (model, treeiter) = selection.get_selected()
            if treeiter:
                path = model.get_path(treeiter)

            store.clear()

            pos = 0
            for playlist in playlists:
                if not playlist.startswith("_"):
                    if playlist == current:
                        store.append(["<b>" + GLib.markup_escape_text(playlist) + "</b>"])
                        cur = pos
                    else:
                        store.append([GLib.markup_escape_text(playlist)])
                    pos = pos + 1

            # restore selection
            if treeiter:
                if path.get_indices()[0] == pos:
                    path.prev()
                if path.get_indices()[0] != -1:
                    selection.select_path(path)

            # scroll to current playlist
            view.scroll_to_cell(cur, None, True, 0.45, 0.0)

    def get_playlist(self):
        self.xmms_async.playlist_current_pos(cb=self.got_current_track)

    def got_current_track(self, result):
        if result.is_error():
            self.current_track = -1
        else:
            self.current_track = result.value()["position"]

        self.xmms_async.playlist_list_entries(cb=self.got_ids)

    def got_ids(self, result):
        if result.is_error():
            print(result.value())
        else:
            ids = result.value()

            fetch = {
                "type": "cluster-list",
                "cluster-by": "position",
                "cluster-field": "",
                "data": {
                    "type": "metadata",
                    "get": ["value"],
                    "fields": ["artist", "album", "title"],
                    "aggregate": "list"
                }
            }

            self.xmms_async.coll_query(xmmsclient.collections.IDList(ids), fetch, self.got_tracks)

    def got_tracks(self, result):
        store = window.playlist_tv.get_model()
        view = window.playlist_tv
        current = self.current_track
        selection = window.playlist_tv.get_selection()

        if result.is_error():
            print(result.value())
        else:
            tracks = result.value()

            # store selection
            (model, treeiter) = selection.get_selected()
            if treeiter:
                path = model.get_path(treeiter)

            store.clear()

            pos = 0
            for track in tracks:
                entry = self.get_title(track)
                if pos == current:
                    entry = "<b>" + entry + "</b>"
                entry += "\n<small>from <i>" + self.get_album(track) + "</i>"
                entry += " by <i>" + self.get_artist(track) + "</i></small>"

                store.append([entry])
                pos = pos + 1

            # restore selection
            if treeiter:
                if path.get_indices()[0] == pos:
                    path.prev()
                if path.get_indices()[0] != -1:
                    selection.select_path(path)

            # scroll to current track
            if current != -1:
                view.scroll_to_cell(current, None, True, 0.45, 0.0)

            self.update = False

    def get_artist(self, info):
        try:
            string = info[0]
        except IndexError:
            string = "none"

        return GLib.markup_escape_text(string)

    def get_album(self, info):
        try:
            string = info[1]
        except IndexError:
            string = "none"

        return GLib.markup_escape_text(string)

    def get_title(self, info):
        try:
            string = info[2]
        except IndexError:
            string = "none"

        return GLib.markup_escape_text(string)

    def jump_to(self, pos):
        self.xmms_async.playlist_set_next(pos)
        self.xmms_async.playback_tickle()
        if self.xmms_async.playback_status != xmmsclient.PLAYBACK_STATUS_PLAY:
            self.xmms_async.playback_start()

    def setup_playlists_cb(self, func):
        # add/remove playlist
        self.xmms_async.broadcast_collection_changed(func)
        # switch playlist
        self.xmms_async.broadcast_playlist_loaded(func)

    def setup_playlist_cb(self, func):
        self.xmms_async.broadcast_playlist_changed(func)
        self.xmms_async.broadcast_playlist_current_pos(func)
        self.xmms_async.broadcast_playlist_loaded(func)

    def remove_playlist(self, name):
        if name != "":
            self.xmms_async.playlist_remove(name)

    def remove_playlist_entry(self, position):
        if position != -1:
            self.xmms_async.playlist_remove_entry(position)

    def remove_playlist_entries(self, positions):
        for position in positions:
            self.xmms_async.playlist_remove_entry(position)

    def playlist_clear(self, widget, playlist):
        self.xmms_async.playlist_clear(playlist)

    def playlist_remove(self, widget, playlist):
        self.xmms_async.playlist_remove(playlist)

    def playlist_create(self, playlist):
        self.xmms_async.playlist_create(playlist)

    def daemon_quit(self):
        self.xmms_async.quit()

    def disconnect(self, xmms_loop):
        print("error: xmms2d shutdown")
        loop.quit()

def remove_pango(data):
    regex = re.compile(r'<.*?>')
    return regex.sub('', data)

class Config():

    # defaults
    autostart = "True"
    autostop = "False"
    maximize = "False"
    skip_taskbar = "False"

    def __init__(self, filename):

        try:
            config = open(filename, "r")
        except IOError:
            config = open(filename, "w+")
            test = configparser.SafeConfigParser()
            test.optionxform = str
            test.add_section("main")
            test.set("main", "SERVER_AUTOSTART", self.autostart)
            test.set("main", "SERVER_SHUTDOWN", self.autostop)
            test.set("main", "MAXIMIZE", self.maximize)
            test.set("main", "SKIP_TASKBAR", self.skip_taskbar)
            test.write(config)
            config.close()
            return

        parser = configparser.SafeConfigParser()
        parser.optionxform = str
        parser.readfp(config)

        changed = False

        if not parser.has_section("main"):
            parser.add_section("main")
            changed = True

        try:
            self.autostart = parser.get("main", "SERVER_AUTOSTART")
        except configparser.NoOptionError:
            parser.set("main", "SERVER_AUTOSTART", self.autostart)
            changed = True

        try:
            self.autostop = parser.get("main", "SERVER_SHUTDOWN")
        except configparser.NoOptionError:
            parser.set("main", "SERVER_SHUTDOWN", self.autostop)
            changed = True

        try:
            self.maximize = parser.get("main", "MAXIMIZE")
        except configparser.NoOptionError:
            parser.set("main", "MAXIMIZE", self.maximize)
            changed = True

        try:
            self.skip_taskbar = parser.get("main", "SKIP_TASKBAR")
        except configparser.NoOptionError:
            parser.set("main", "SKIP_TASKBAR", self.skip_taskbar)
            changed = True

        config.close()

        if changed:
            config = open(filename, "w+")
            parser.write(config)
            config.close()

    def get_autostart(self):
        if self.autostart == "True":
            return True
        else:
            return False

    def get_autostop(self):
        if self.autostop == "True":
            return True
        else:
            return False

    def get_maximize(self):
        if self.maximize == "True":
            return True
        else:
            return False

    def get_skip_taskbar(self):
        if self.skip_taskbar == "True":
            return True
        else:
            return False

def signal_handler(signum, frame):
    window.toggle()

if __name__ == "__main__":
    global config
    global loop
    global connection
    global window
    global icon

    global iconname
    iconname = "/usr/share/pixmaps/lwxc.svg"

    #global config_path
    config_path = os.getenv("XDG_CONFIG_HOME") + "/xmms2/clients/lwxc/"

    parser = optparse.OptionParser()

    parser.add_option("-i", "--instance",
                      action="store", dest="instance", default="default",
                      help="name of instance")

    (options, args) = parser.parse_args()

    pid_file = config_path + options.instance + ".pid"


    if not os.path.exists(config_path):
        os.makedirs(config_path)

    # handle pid file
    try:
        pid_fd = os.open(pid_file, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o0600)
    except OSError:
        #print("pidfile already exists")
        try:
            pidfile = open(pid_file, 'r')
        except IOError:
            print("error opening pidfile")
            sys.exit(1)
        try:
            #print("going to toggle")
            os.kill(int(pidfile.readline()), signal.SIGUSR1)
            pidfile.close()
            sys.exit(0)
        except OSError:
            #print("no instance is running")
            try:
                os.remove(pid_file)
            except OSError:
                print("error removing pidfile")
                sys.exit(1)
            try:
                pid_fd = os.open(pid_file, os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o0600)
            except OSError:
                print("persistent error with pidfile, giving up")
                sys.exit(1)

    pid = os.fdopen(pid_fd, 'w')
    try:
        pid.write(str(os.getpid()))
        pid.close()
    except IOError:
        pass


    try:
        config = Config(config_path + options.instance + ".conf")

        loop = GObject.MainLoop(None, False)

        connection = Connection()
        window = window_main(options.instance)
        icon = TrayIcon()

        signal.signal(signal.SIGUSR1, signal_handler)

        loop.run()

    except KeyboardInterrupt:
        loop.quit()

    try:
        os.remove(pid_file)
    except OSError:
        pass

    if config.get_autostop():
        connection.daemon_quit()

