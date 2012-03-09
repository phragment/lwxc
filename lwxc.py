#!/usr/bin/env python2
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

"""
TODO
 - check playlist sort
 - check add titles to playlist, selection workaround
 - rewrite use of collections
 - after delete (from playlist) select next
 - placement on unhide (pidgin!)
 - replace result.get_error() with result.value() (for async only?)
 - replace cgi with glib.markup_escape_text
 - control already running instance (show/hide)

later?
 - drap & drop
  - reordering of playlist
  - add to playlist
 - seekbar
"""

import pygtk
#pygtk.require("2.0")
import gtk
import os
import sys
import xmmsclient
from xmmsclient import collections
import xmmsclient.glib
import gobject
import cgi
import time
import re
import ConfigParser

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
    playlist = None

    playlist_changing = False

    artists_selection = []
    artists_selection_prev = []
    albums_selection = []
    albums_selection_prev = []
    tracks_selection = []
    tracks_selection_prev = []

    # TODO
    dialog = None
    dialog_entry = None

    def __init__(self):

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("delete-event", self.on_delete_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        self.window.connect("configure-event", self.on_configure_event)
        self.window.connect("key-press-event", self.on_key_press_event)
        self.window.set_title("le wild xmms2 client")
        self.window.set_icon_from_file("/usr/share/pixmaps/xmms2.svg")
        self.window.set_size_request(800, 500)
        self.window.set_position(gtk.WIN_POS_CENTER)

        if config.get_maximize():
            self.window.maximize()

        vbox1 = gtk.VBox(False, 0)
        self.window.add(vbox1)

        menubar = gtk.MenuBar()
#        vbox1.pack_start(menubar, False, False, 0)

        ag = gtk.AccelGroup()
        self.window.add_accel_group(ag)

        menubar_file = gtk.MenuItem("_File")
        menubar.append(menubar_file)

        file_menu = gtk.Menu()
        menubar_file.set_submenu(file_menu)

        file_menu_quit = gtk.ImageMenuItem(gtk.STOCK_QUIT, ag)
        file_menu.append(file_menu_quit)
        file_menu_quit.connect("activate", self.quit)

        menubar_help = gtk.MenuItem("_Help")
        menubar.append(menubar_help)

        help_menu = gtk.Menu()
        menubar_help.set_submenu(help_menu)

        help_menu_about = gtk.ImageMenuItem(gtk.STOCK_ABOUT, ag)
        help_menu.append(help_menu_about)
        help_menu_about.connect("activate", self.show_about_dialog)

        hbox1 = gtk.HBox(False, 0)
        vbox1.pack_start_defaults(hbox1)

        artists_sw = gtk.ScrolledWindow()
        artists_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox1.pack_start_defaults(artists_sw)


        artists_tv = gtk.TreeView()

        cel = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Artists", cel, text=0)
        artists_tv.append_column(col)
        artists_tv.set_headers_visible(False)

        self.artists_sel = artists_tv.get_selection()
        self.artists_sel.set_mode(gtk.SELECTION_MULTIPLE)
        self.artists_sel.connect("changed", self.on_artists_selection_changed)

        self.artists = gtk.ListStore(str)
        artists_tv.set_model(self.artists)

        artists_tv.connect("row-activated", self.on_artists_activated)

        artists_sw.add(artists_tv)

        connection.get_artists(self.artists)


        vsep1 = gtk.VSeparator()
        hbox1.pack_start(vsep1, False, False, 0)

        albums_sw = gtk.ScrolledWindow()
        albums_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox1.pack_start_defaults(albums_sw)


        albums_tv = gtk.TreeView()

        cel = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Albums", cel, text=0)
        albums_tv.append_column(col)
        albums_tv.set_headers_visible(False)

        self.albums_sel = albums_tv.get_selection()
        self.albums_sel.set_mode(gtk.SELECTION_MULTIPLE)
        self.albums_sel.connect("changed", self.on_albums_selection_changed)

        self.albums = gtk.ListStore(str)
        albums_tv.set_model(self.albums)

        albums_tv.connect("row-activated", self.on_albums_activated)

        albums_sw.add(albums_tv)


        vsep2 = gtk.VSeparator()
        hbox1.pack_start(vsep2, False, False, 0)

        tracks_sw = gtk.ScrolledWindow()
        tracks_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox1.pack_start_defaults(tracks_sw)


        tracks_tv = gtk.TreeView()

        cel = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Tracks", cel, text=0)
        tracks_tv.append_column(col)
        tracks_tv.set_headers_visible(False)

        self.tracks_sel = tracks_tv.get_selection()
        self.tracks_sel.set_mode(gtk.SELECTION_MULTIPLE)
        self.tracks_sel.connect("changed", self.on_tracks_selection_changed)

        self.tracks = gtk.ListStore(str)
        tracks_tv.set_model(self.tracks)

        tracks_tv.connect("row-activated", self.on_tracks_activated)

        tracks_sw.add(tracks_tv)


        vsep3 = gtk.VSeparator()
        hbox1.pack_start(vsep3, False, False, 0)

        vbox2 = gtk.VBox(False, 0)
        hbox1.pack_end_defaults(vbox2)

        playlists_sw = gtk.ScrolledWindow()
        playlists_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox2.pack_start(playlists_sw, False, False, 0)


        self.playlists_tv = gtk.TreeView()

        cel = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Artists", cel, markup=0)
        self.playlists_tv.append_column(col)
        self.playlists_tv.set_headers_visible(False)

        self.playlists_sel = self.playlists_tv.get_selection()
        self.playlists_sel.set_mode(gtk.SELECTION_SINGLE)

        self.playlists = gtk.ListStore(str)
        self.playlists_tv.set_model(self.playlists)

        self.playlists_tv.connect("row-activated", self.on_playlists_activated)
        self.playlists_tv.connect("key-press-event", self.on_playlists_key_press)
        self.playlists_tv.connect("button-press-event", self.on_playlists_button_press)

        playlists_sw.add(self.playlists_tv)

        connection.get_playlists(self.playlists)


        hsep1 = gtk.HSeparator()
        vbox2.pack_start(hsep1, False, False, 0)

        playlist_sw = gtk.ScrolledWindow()
        playlist_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vbox2.pack_start_defaults(playlist_sw)


        playlist_tv = gtk.TreeView()

        cel = gtk.CellRendererText()
        col = gtk.TreeViewColumn("Playlist", cel, markup=0)
        playlist_tv.append_column(col)
        playlist_tv.set_headers_visible(False)

        playlist_sel = playlist_tv.get_selection()
        playlist_sel.set_mode(gtk.SELECTION_SINGLE)

        self.playlist = gtk.ListStore(str)
        playlist_tv.set_model(self.playlist)

        playlist_tv.connect("row-activated", self.on_playlist_activated)
        playlist_tv.connect("key-press-event", self.on_playlist_key_press)

        playlist_sw.add(playlist_tv)

        connection.get_playlist(self.playlist)


#        hbox2 = gtk.HBox(False, 0)
#        vbox1.pack_start(hbox2, False, False, 0)

#        seekbar = gtk.HScale()
#        hbox2.pack_start_defaults(seekbar)
#        seekbar.set_draw_value(False)

#        volume = gtk.VolumeButton()
#        hbox2.pack_start(volume, False, False, 0)


        vbox1.show_all()

        # callbacks
        connection.setup_playlists_cb(self.on_playlists_changed)
        connection.setup_playlist_cb(self.on_playlist_changed)

    def quit(self, widget):
        loop.quit()

    def toggle(self, widget):
        if self.window.get_property("visible"):
            # conflicts with position
            # even restores workspace?!
            self.pos_x, self.pos_y = self.window.get_position()
            self.window.hide()
        else:
            self.window.deiconify()
            self.window.show()
            if self.pos_x != -1:
                self.window.move(self.pos_x, self.pos_y)

    def on_delete_event(self, widget, event):
        self.window.hide()
        return True

    def on_window_state_event(self, widget, event):
        if event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.window.hide()

    def on_configure_event(self, widget, event):
        if not self.playlists_tv:
            return

        (width, height) = self.window.get_size()
        new_height = height/100*15
        self.playlists_tv.set_size_request(0, new_height)

    def on_key_press_event(self, window, event):

        if event.keyval == gtk.keysyms.Right:
            self.window.get_toplevel().child_focus(gtk.DIR_TAB_FORWARD) 

        if event.keyval == gtk.keysyms.Left:
            self.window.get_toplevel().child_focus(gtk.DIR_TAB_BACKWARD) 

    def on_artists_selection_changed(self, treeview):
        self.artists_selection_prev = self.artists_selection
        (model, pathlist) = self.artists_sel.get_selected_rows()
        self.artists_selection = pathlist

        # TODO
        # make list comprehension
        artists = []
        for path in pathlist:
            iter = model.get_iter(path)
            artists.append(model.get_value(iter, 0))

        connection.get_albums(self.albums, artists)

    def on_albums_selection_changed(self, treeview):
        self.albums_selection_prev = self.albums_selection
        (model, pathlist) = self.albums_sel.get_selected_rows()
        self.albums_selection = pathlist

        # TODO
        # make list comprehension
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
            # workaround
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
            # workaround
            selection.select_path(path)

        connection.add_albums(albums)

    def on_tracks_activated(self, treeview, iter, path):
        selection = treeview.get_selection()
        (model, pathlist) = selection.get_selected_rows()

        #print pathlist
        pathlist = self.tracks_selection_prev
        #print pathlist

        tracks = []
        for path in pathlist:
            iter = model.get_iter(path)
            tracks.append(model.get_value(iter, 0))
            # important part of workaround!
            selection.select_path(path)

        #print tracks

        connection.add_tracks(tracks)

    def on_playlists_activated(self, treeview, iter, path):
        (model, iter) = self.playlists_sel.get_selected()
        connection.load_playlist(model.get_value(iter, 0))

    def on_playlist_activated(self, treeview, iter, path):
        connection.jump_to(iter[0])

    def on_playlists_key_press(self, treeview, event):
        if event.keyval == gtk.keysyms.Menu:
            # stop signal or menu disappears
            treeview.stop_emission("key_press_event")

            selection = treeview.get_selection()
            (model, iter) = selection.get_selected()

            name = model.get_value(iter, 0)

            self.on_playlists_menu(treeview, 0, event.time, name)

        if event.keyval == gtk.keysyms.Delete:

            print "disabled"
            return

            selection = treeview.get_selection()
            (model, iter) = selection.get_selected()

            name = model.get_value(iter, 0)

            connection.remove_playlist(name)

    def on_playlists_button_press(self, treeview, event):
        if event.button == 3:
            pthinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

            name = None
            pos = None

            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                model = treeview.get_model()
                iter = model.get_iter(path)
                name = model.get_value(iter, 0)
                treeview.set_cursor(path, col, 0)

            self.on_playlists_menu(treeview, event.button, event.time, name)

    def on_playlist_key_press(self, treeview, event):
        if event.keyval == gtk.keysyms.Delete:

            selection = treeview.get_selection()
            (model, iter) = selection.get_selected()

            if not iter:
                return

            path = model.get_path(iter)

            connection.remove_playlist_entry(path[0])

    def on_playlists_changed(self, result):
        connection.get_playlists(self.playlists)

    # solve via callbacks?! (maybe coll_add cd?)
    def on_playlist_changed(self, result):
#        print "stage 1"
        # poor mans lock
        if self.playlist_changing:
            return
        self.playlist_changing = True
        #time.sleep(0.1)

#        print "stage 2"
        connection.get_playlist(self.playlist)

        self.playlist_changing = False



    # cannot remove current active playlist (xmms2 limitation)
    def on_playlists_menu(self, treeview, button, time, playlist):

        menu = gtk.Menu()

        # playlist can be None
        if playlist is not None:
            playlist = remove_pango(playlist)
            
            clear = gtk.MenuItem("clear \'" + playlist + "\'")
            clear.connect("activate", connection.playlist_clear, playlist)
            menu.append(clear)

            remove = gtk.MenuItem("remove \'" + playlist + "\'")
            remove.connect("activate", connection.playlist_remove, playlist)
            menu.append(remove)

            #copy = gtk.MenuItem("copy " + playlist)
            #copy.connect("activate", self.to_be_implemented_handler)
            #menu.append(copy)

            #rename = gtk.MenuItem("rename " + playlist)
            #rename.connect("activate", self.to_be_implemented_handler)
            #menu.append(rename)

        create = gtk.MenuItem("new playlist")
        create.connect("activate", self.show_text_entry_dialog)
        menu.append(create)

        selection = treeview.get_selection()
        (model, iter) = selection.get_selected()

        path = model.get_path(iter)

        cell_area = treeview.get_cell_area(path, treeview.get_column(0))

        x, y = treeview.get_bin_window().get_origin()
        y += cell_area.y

        menu.show_all()
        menu.popup(None, None, self.position_menu, button, time, (x, y))

    def position_menu(window, menu, data):
        (x, y) = data
        return (x, y, True)

    def show_about_dialog(self, widget):
        about_dialog = gtk.AboutDialog()

        about_dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        about_dialog.set_transient_for(self.window)

        about_dialog.set_name("le wild xmms2 client")
        about_dialog.set_version("0.1")
        #about_dialog.set_comments("Ein einfacher Medien-Bibliothek Browser für XMMS2, mit Fokus auf Tastaturbedienbarkeit.")
        about_dialog.set_comments("A simple media library browser for XMMS2, with a focus on keyboard operability.")
        #about_dialog.set_authors(["Thomas Krug"])
        about_dialog.set_copyright("Copyright © 2012 Thomas Krug")
        about_dialog.set_website("http://phragment.github.com/lwxc/")
        about_dialog.set_website_label("phragment.github.com/lwxc")

        about_dialog.set_logo(gtk.gdk.pixbuf_new_from_file_at_size("/usr/share/pixmaps/xmms2.svg", 200, 200))

        about_dialog.run()
        about_dialog.destroy()

    def show_text_entry_dialog(self, widget):
        self.dialog = gtk.Dialog("new playlist", self.window, gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT)
        self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.dialog.set_size_request(300, 80)

        label = gtk.Label("Please enter name:")
        self.dialog.vbox.pack_start_defaults(label)

        self.dialog_entry = gtk.Entry()
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
            print "no entry"
            return

        connection.playlist_create(text)


#class TrayIcon(window, connection):
class TrayIcon():

    icon = None
    menu = None

    def __init__(self):
        self.icon = gtk.StatusIcon()
        self.icon.set_from_file("/usr/share/pixmaps/xmms2.svg")
        self.icon.connect("activate", window.toggle)
        self.icon.connect("popup-menu", self.on_popup_menu)

        self.menu = gtk.Menu()

        play = gtk.MenuItem("Play")
        play.connect("activate", connection.play)
        self.menu.append(play)

        pause = gtk.MenuItem("Pause")
        pause.connect("activate", connection.pause)
        self.menu.append(pause)

        stop = gtk.MenuItem("Stop")
        stop.connect("activate", connection.stop)
        self.menu.append(stop)

        sep1 = gtk.SeparatorMenuItem()
        self.menu.append(sep1)

        prev = gtk.MenuItem("Prev")
        prev.connect("activate", connection.prev)
        self.menu.append(prev)

        next = gtk.MenuItem("Next")
        next.connect("activate", connection.next)
        self.menu.append(next)

        sep1 = gtk.SeparatorMenuItem()
        self.menu.append(sep1)

        about = gtk.MenuItem("About")
        about.connect("activate", window.show_about_dialog)
        self.menu.append(about)

        quit = gtk.MenuItem("Quit")
        quit.connect("activate", self.quit)
        self.menu.append(quit)

    def quit(self, widget):
        loop.quit()

    def on_popup_menu(self, icon, button, time):
        self.menu.show_all()
        self.menu.popup(None, None, None, button, time)


class Connection:

    xmms = None
    xmms_async = None

    def __init__(self):
        if config.get_autostart():
            print "starting xmms2"
            os.system("xmms2-launcher")

        self.xmms_async = xmmsclient.XMMS("lwxc")
        try:
            self.xmms_async.connect(os.getenv("XMMS_PATH"), disconnect_func=self.disconnect)
        except IOError, detail:
            print "Connection failed:", detail
            sys.exit(1)

        self.xmms = xmmsclient.XMMSSync("lwxc")
        self.xmms.connect(os.getenv("XMMS_PATH"))

        conn = xmmsclient.glib.GLibConnector(self.xmms_async)

    def play(self, widget):
        try:
            self.xmms.playback_start()
        except XMMSError, detail:
            print "Error: ", detail.message

    def pause(self, widget):
        self.xmms.playback_pause()

    def stop(self, widget):
        self.xmms.playback_stop()

    def next(self, widget):
        self.xmms.playlist_set_next_rel(1)
        self.xmms.playback_tickle()
        if self.xmms.playback_status != xmmsclient.PLAYBACK_STATUS_PLAY:
            self.xmms.playback_start()

    def prev(self, widget):
        self.xmms.playlist_set_next_rel(-1)
        self.xmms.playback_tickle()
        if self.xmms.playback_status != xmmsclient.PLAYBACK_STATUS_PLAY:
            self.xmms.playback_start()

    def add_artists(self, artists):
        coll = collections.IDList()
        for artist in artists:
            coll = coll | collections.Match(field="artist", value=artist)

#        result = self.xmms_async.playlist_clear()
#        result.wait()
#        if result.iserror():
#            print "error: ", result.get_error()

        result = self.xmms_async.playlist_add_collection(coll, ['artist', 'date', 'album', 'tracknr', 'title'])
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

    def add_albums(self, albums):
        coll = collections.IDList()
        for album in albums:
            coll = coll | collections.Match(field="album", value=album)

        result = self.xmms_async.playlist_add_collection(coll, ['artist', 'date', 'album', 'tracknr', 'title'])
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

    def dummy(self, value):
        print "dummy"

    # TODO
    # on tracks.size() > 1
    # "Failed in file ../src/lib/xmmstypes/value.c on  row 305"
    def add_tracks(self, tracks):
#        coll = collections.IDList()
        for track in tracks:
#            coll = coll | collections.Match(field="title", value=track)
            coll = collections.Match(field="title", value=track)
            #self.xmms_async.playlist_add_collection(coll, ["artist", "date", "album", "tracknr", "title"], cb=self.dummy)
            self.xmms_async.playlist_add_collection(coll, ["artist", "date", "album", "tracknr", "title"])

#        self.xmms_async.playlist_add_collection(coll, ["artist", "date", "album", "tracknr", "title"], cb=self.dummy)

    # TODO reuse collection on get_* functions
    def get_artists(self, store):
        artists = collections.Match(field="artist", value="*")

        result = self.xmms_async.coll_query_infos(artists, ["artist"], order=["artist"])
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

        store.clear()
        for artist in result.value():
            store.append([artist["artist"]])

    def get_albums(self, store, artists):
        if not store:
            return

        albums = collections.IDList()
        for artist in artists:
            albums = albums | collections.Match(field="artist", value=artist)

        result = self.xmms_async.coll_query_infos(albums, ["album"], order=["artist", "date", "album"])
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

        store.clear()
        for album in result.value():
            store.append([album["album"]])

    def get_tracks(self, store, albums):
        if not store:
            return

        tracks = collections.IDList()
        for album in albums:
            tracks = tracks | collections.Match(field="album", value=album)

        result = self.xmms_async.coll_query_infos(tracks, ["title"], order=['artist', 'date', 'album', 'tracknr', 'title'])
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

        store.clear()
        for title in result.value():
            store.append([title["title"]])

    def load_playlist(self, meh):
        try:
            self.xmms.playlist_load(meh)
        except xmmsclient.sync.XMMSError:
            pass

    def get_playlist(self, store):
        result = self.xmms.playlist_list_entries()

        pos_cur = self.get_playlist_cur_pos()

        store.clear()

        pos = 0
        for id in result:
            bar = self.get_title(self.get_info(id))
            if pos == pos_cur:
                bar = "<b>" + bar + "</b>"
            bar += "\n<small>from <i>" + self.get_album(self.get_info(id)) + "</i>"
            bar += " by <i>" + self.get_artist(self.get_info(id)) + "</i></small>"

            store.append([bar])
            pos = pos + 1

    # TODO this should be a class
    def get_info(self, id):
        result = self.xmms_async.medialib_get_info(id)
        result.wait()
        if result.iserror():
            print "error: ", result.get_error()

        return result.value()

    def get_artist(self, info):
        try:
            string = info["artist"]
        except KeyError:
            string = "none"

        return cgi.escape(string)

    def get_album(self, info):
        try:
            string = info["album"]
        except KeyError:
            string = "none"

        return cgi.escape(string)

    def get_title(self, info):
        try:
            string = info["title"]
        except KeyError:
            string = "none"

        return cgi.escape(string)

    def get_year(self, info):
        try:
            string = info["date"]
        except KeyError:
            string = "none"

        return cgi.escape(string)

    def get_track(self, info):
        try:
            string = info["tracknr"]
        except KeyError:
            string = "none"

        return cgi.escape(string)

    # TODO check error handling
    def get_playlist_cur_pos(self):
        pos = 0
        try:
            result = self.xmms.playlist_current_pos()
            try:
                pos = result["position"]
            except xmmsclient.sync.XMMSError:
                pos = 0
        except xmmsclient.sync.XMMSError:
            pass

        return pos

    def get_playlists(self, store):
        result = self.xmms.playlist_list()

        cur = self.get_current_playlist()

        store.clear()

        for playlist in result:
            if not playlist.startswith("_"):
                if playlist == cur:
                    store.append(["<b>" + cgi.escape(playlist) + "</b>"])
                else:
                    store.append([cgi.escape(playlist)])

    def get_current_playlist(self):
        result = self.xmms.playlist_current_active()
        return result

    def jump_to(self, pos):
        self.xmms.playlist_set_next(pos)
        self.xmms.playback_tickle()
        if self.xmms.playback_status != xmmsclient.PLAYBACK_STATUS_PLAY:
            self.xmms.playback_start()

    def setup_playlists_cb(self, func):
        # add/remove playlist
        self.xmms_async.broadcast_collection_changed(func)
        # switch playlist
        self.xmms_async.broadcast_playlist_loaded(func)

    def setup_playlist_cb(self, func):
        self.xmms_async.broadcast_playlist_changed(func)
        self.xmms_async.broadcast_playlist_current_pos(func)
        self.xmms_async.broadcast_playlist_loaded(func)

    # TODO catch error
    # FIXME decide sync
    def remove_playlist(self, name):
        self.xmms.playlist_remove(name)

    def remove_playlist_entry(self, position):
        self.xmms.playlist_remove_entry(position)

    def remove_playlist_entries(self, positions):
        for position in positions:
            self.xmms.playlist_remove_entry(position)

    def playlist_clear(self, widget, playlist):
        result = self.xmms_async.playlist_clear(playlist)
        result.wait()
        if result.is_error():
            print "error: ", result.value()

    # FIXME decide async
    def playlist_remove(self, widget, playlist):
        result = self.xmms_async.playlist_remove(playlist)
        result.wait()
        if result.is_error():
            print "error: ", result.value()

    def playlist_create(self, playlist):
        #playlist_create(playlist, cb=None)
        result = self.xmms_async.playlist_create(playlist)
        result.wait()
        if result.is_error():
            print "error: ", result.value()

    def playlist_rename(self, widget):
        print "to be implemented"

    def playlist_copy(self, widget):
        print "to be implemented"

    def daemon_quit(self):
        result = self.xmms_async.quit()
        result.wait()
        if result.is_error():
            print "error: ", result.value()

    def disconnect(self, res):
        print "error: xmms2d shutdown"
        loop.quit()

def remove_pango(data):
    regex = re.compile(r'<.*?>')
    return regex.sub('', data)

class Config():

    # defaults
    autostart = "True"
    autostop = "False"
    maximize = "False"

    def __init__(self):
        parser = ConfigParser.SafeConfigParser()
#        parser.optionxfrom = str

        # error check
        try:
            config = open(os.getenv("XDG_CONFIG_HOME") + "/xmms2/clients/lwxc.conf")
        except IOError:
            config = open(os.getenv("XDG_CONFIG_HOME") + "/xmms2/clients/lwxc.conf", "w")
            parser.add_section("main")
            parser.set("main", "SERVER_AUTOSTART", self.autostart)
            parser.set("main", "SERVER_AUTOSTOP", self.autostop)
            parser.set("main", "MAXIMIZE", self.maximize)
            parser.write(config)
            config.close

        try:
            config = open(os.getenv("XDG_CONFIG_HOME") + "/xmms2/clients/lwxc.conf")
        except IOError, detail:
            print "Config file error: ", detail
            sys.exit(1)

        parser.readfp(config)
        #config.close()

        self.autostart = parser.get("main", "SERVER_AUTOSTART")
        self.autostop = parser.get("main", "SERVER_AUTOSTOP")
        self.maximize = parser.get("main", "MAXIMIZE")

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

if __name__ == "__main__":
    global config
    global loop
    global connection
    global window
    global icon

    try:
        config = Config()

        loop = gobject.MainLoop(None, False)

        connection = Connection()
        window = window_main()
        icon = TrayIcon()

        loop.run()

    except KeyboardInterrupt:
        loop.quit()

    if config.get_autostop():
        print "stopping xmms2"
        connection.daemon_quit()

