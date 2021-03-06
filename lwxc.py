#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2012-2015 Thomas Krug
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
from gi.repository import Gtk, Gdk, GObject, GLib, GdkPixbuf

import xmmsclient
import xmmsclient.collections

import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop 

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

        self.window = Gtk.Window()
        self.window.connect("delete-event", self.on_delete_event)
        self.window.connect("window-state-event", self.on_window_state_event)
        self.window.connect("configure-event", self.on_configure_event)
        self.window.connect("key-press-event", self.on_key_press_event)
        self.window.set_title("le wild xmms2 client")
        self.window.set_icon_from_file(iconname)
        self.window.set_wmclass(instance, "LWXC")

        screen = self.window.get_screen()
        window_rect = screen.get_monitor_geometry(screen.get_monitor_at_window(screen.get_active_window()))
        width  = window_rect.width  * 0.75
        height = window_rect.height * 0.75
        self.window.set_size_request(int(width), int(height))

        self.window.set_position(Gtk.WindowPosition.CENTER)


        if config.get_maximize():
            self.window.maximize()

        if config.get_skip_taskbar():
            self.window.set_skip_taskbar_hint(True)

        if config.get_force_show():
            self.window.set_keep_above(True)

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

        self.albums_sw = Gtk.ScrolledWindow()
        self.albums_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox1.pack_start(self.albums_sw, True, True, 0)


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

        self.albums_sw.add(albums_tv)


        vsep2 = Gtk.VSeparator()
        hbox1.pack_start(vsep2, False, False, 0)

        self.tracks_sw = Gtk.ScrolledWindow()
        self.tracks_sw.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        hbox1.pack_start(self.tracks_sw, True, True, 0)


        self.tracks_tv = Gtk.TreeView()

        cel = Gtk.CellRendererText()
        col = Gtk.TreeViewColumn("Tracks", cel, text=0)
        self.tracks_tv.append_column(col)
        self.tracks_tv.set_headers_visible(False)

        self.tracks_sel = self.tracks_tv.get_selection()
        self.tracks_sel.set_mode(Gtk.SelectionMode.MULTIPLE)
        self.tracks_sel.connect("changed", self.on_tracks_selection_changed)

        self.tracks = Gtk.ListStore(str)
        self.tracks_tv.set_model(self.tracks)

        self.tracks_tv.connect("row-activated", self.on_tracks_activated)

        self.tracks_sw.add(self.tracks_tv)

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

        self.playlists_tv.connect("button-press-event", self.on_playlists_button_press)
        self.playlists_tv.connect("key-press-event", self.on_playlists_key_press)

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

        self.playlist_tv.connect("button-press-event", self.on_playlist_button_press)
        self.playlist_tv.connect("key-press-event", self.on_playlist_key_press)

        self.playlist_sw.add(self.playlist_tv)

        # focus
        self.playlist_tv.grab_focus()

        connection.get_playlist()


        hbox2 = Gtk.HBox(False, 0)
        # remove all widgets in bottom box from focus chain
        hbox2.set_focus_chain([])
        vbox1.pack_start(hbox2, False, False, 0)

        prev_img = Gtk.Image()
        prev_img.set_from_stock(Gtk.STOCK_MEDIA_PREVIOUS, Gtk.IconSize.BUTTON)
        prev = Gtk.Button(image=prev_img)
        prev.connect("clicked", connection.prev)
        hbox2.pack_start(prev, False, False, 0)

        self.pp_img = Gtk.Image()
        self.pp = Gtk.Button()
        hbox2.pack_start(self.pp, False, False, 0)

        stop_img = Gtk.Image()
        stop_img.set_from_stock(Gtk.STOCK_MEDIA_STOP, Gtk.IconSize.BUTTON)
        stop = Gtk.Button(image=stop_img)
        stop.connect("clicked", connection.stop)
        hbox2.pack_start(stop, False, False, 0)

        nxt_img = Gtk.Image()
        nxt_img.set_from_stock(Gtk.STOCK_MEDIA_NEXT, Gtk.IconSize.BUTTON)
        nxt = Gtk.Button(image=nxt_img)
        nxt.connect("clicked", connection.next_)
        hbox2.pack_start(nxt, False, False, 0)


        elapsed_eb = Gtk.EventBox()
        self.elapsed = Gtk.Label("0:00")
        elapsed_eb.add(self.elapsed)
        elapsed_eb.connect("button-press-event", self.seek_backwards)
        hbox2.pack_start(elapsed_eb, False, False, 0)

        self.adj = Gtk.Adjustment()
        self.adj.set_step_increment(1000)
        self.adj.set_page_increment(10000)
        self.scale = Gtk.HScale(adjustment=self.adj)
        self.scale.set_draw_value(False)
        self.scale.connect("change-value", self.seek)
        self.scale.connect("value-changed", self.seek_pos)
        hbox2.pack_start(self.scale, True, True, 0)

        self.scale.connect("button-press-event", self.scale_on_button_press)
        self.scale.connect("button-release-event", self.scale_on_button_release)
        self.scale_ignore_updates = False
        self.scale_value = -1

        duration_eb = Gtk.EventBox()
        self.duration = Gtk.Label("0:00")
        duration_eb.add(self.duration)
        duration_eb.connect("button-press-event", self.seek_forwards)
        hbox2.pack_start(duration_eb, False, False, 0)


        self.volume = Gtk.VolumeButton()
        hbox2.pack_start(self.volume, False, False, 0)

        self.volume.connect("value-changed", self.vol)

        self.vol_adj = self.volume.get_adjustment()
        self.vol_adj.set_lower(0)
        self.vol_adj.set_upper(100)
        self.vol_adj.set_step_increment(5)
        self.vol_adj.set_page_increment(10)
        self.vol_adj.set_value(connection.get_volume())

        vbox1.show_all()

        connection.setup_playlists_cb(self.on_playlists_changed)
        connection.setup_playlist_cb(self.on_playlist_changed)
        connection.setup_playtime_cb(self.on_playtime_changed)
        connection.setup_volume_cb(self.on_volume_changed)
        connection.setup_playback_cb(self.on_playback_changed)

    def on_volume_changed(self, volume):
        self.vol_adj.set_value(volume)

    def seek(self, widget, scroll, value):
        self.scale_value = value

    def seek_backwards(self, widget, event):
        connection.seek_backwards(30000)

    def seek_forwards(self, widget, event):
        connection.seek_forwards(30000)

    def scale_on_button_press(self, widget, event):
        self.scale_ignore_updates = True
        self.scale_ct = connection.current_track

    def scale_on_button_release(self, widget, event):
        self.scale_ignore_updates = False
        if self.scale_value > 0:
            if self.scale_ct == connection.current_track:
                connection.seek(self.scale_value)
        self.scale_value = -1

    def seek_pos(self, widget):
        self.elapsed.set_text(self.mstostr(widget.get_value()))

    def vol(self, widget, value):
        connection.set_volume(value)

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
        # enable Left/Right keys

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

    def on_playlists_key_press(self, treeview, event):

        if event.keyval == Gdk.KEY_Menu:
            self.playlists_menu(treeview, None)

        if event.keyval == Gdk.KEY_Return:
            connection.load_playlist(get_selected_entry(treeview))
            self.playlist_tv.grab_focus()

    def on_playlists_button_press(self, treeview, event):

        if event.button == 1:
            if event.type == Gdk.EventType._2BUTTON_PRESS:
                connection.load_playlist(get_selected_entry(treeview))
                self.playlist_tv.grab_focus()

        if event.button == 3:
            pthinfo = treeview.get_path_at_pos(int(event.x), int(event.y))

            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.set_cursor(path, col, 0)

            self.playlists_menu(treeview, event)

    def on_playlist_key_press(self, treeview, event):

        if event.keyval == Gdk.KEY_Delete:
            connection.remove_playlist_entry(get_selected_entry_position(treeview))

        if event.keyval == Gdk.KEY_Return:
            connection.jump_to(get_selected_entry_position(treeview))

    def on_playlist_button_press(self, treeview, event):

        if event.button == 1:
            if event.type == Gdk.EventType._2BUTTON_PRESS:
                connection.jump_to(get_selected_entry_position(treeview))

    def on_playlists_changed(self, result):
        connection.get_playlists()

    def on_playlist_changed(self, result):

        # meh, partial updates would need a far more sophisticated model
        if not connection.update:
            connection.get_playlist()

    def on_playtime_changed(self, elapsed, duration):
        if self.scale_ignore_updates:
            return

        self.scale.set_range(0, duration)
        self.adj.set_lower(0)
        self.adj.set_upper(duration)
        self.adj.set_value(elapsed)

        self.elapsed.set_text(self.mstostr(elapsed))
        self.duration.set_text(self.mstostr(duration))

    def mstostr(self, ms):
        m, s = divmod(ms/1000, 60)
        h, m = divmod(m, 60)
        fmt = str(int(m)).zfill(2) + ':' + str(int(s)).zfill(2)
        if h:
            fmt = str(int(h)) + ':' + fmt
        return ' ' + fmt + ' '

    def on_playback_changed(self, status):
        if status == xmmsclient.PLAYBACK_STATUS_PLAY:
            img = Gtk.Image()
            img.set_from_stock(Gtk.STOCK_MEDIA_PAUSE, Gtk.IconSize.BUTTON)
            self.pp.set_image(img)
            self.pp.connect("clicked", connection.pause)
        else:
            img = Gtk.Image()
            img.set_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON)
            self.pp.set_image(img)
            self.pp.connect("clicked", connection.play)

        if status == xmmsclient.PLAYBACK_STATUS_STOP:
            self.scale.set_sensitive(False)
            self.elapsed.set_text(self.mstostr(0))
            self.adj.set_value(0)
        else:
            self.scale.set_sensitive(True)

    def playlists_menu(self, treeview, event):

        # get selected playlist
        selection = treeview.get_selection()
        (model, it) = selection.get_selected()
        if it:
            playlist = model.get_value(it, 0)

        # build popup menu
        menu = Gtk.Menu()

        create = Gtk.MenuItem("create new playlist")
        create.connect("activate", self.show_text_entry_dialog)
        menu.append(create)

        # add items if playlist selected
        if it:
            playlist = remove_pango(playlist)

            clear = Gtk.MenuItem("clear playlist: " + playlist)
            clear.connect("activate", connection.playlist_clear, playlist)
            menu.append(clear)

            if connection.current_playlist != playlist:
                remove = Gtk.MenuItem("remove playlist: " + playlist)
                remove.connect("activate", connection.remove_playlist, playlist)
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

        about_dialog.set_program_name("le wild xmms2 client")
        about_dialog.set_version("0.2")
        about_dialog.set_comments("A simple media library browser for XMMS2,\nwith a focus on keyboard operability.")
        about_dialog.set_copyright("Copyright © 2012 Thomas Krug")
        about_dialog.set_website("http://phragment.github.com/lwxc/")
        about_dialog.set_website_label("phragment.github.com/lwxc")

        about_dialog.set_logo(GdkPixbuf.Pixbuf.new_from_file_at_size(iconname, 200, 200))

        about_dialog.run()
        about_dialog.destroy()

    def show_text_entry_dialog(self, widget):
        self.dialog = Gtk.Dialog("create new playlist", self.window, Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT)
        self.dialog.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.dialog.set_size_request(300, 60)

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

    xmms = None
    xmms_async = None

    update = False

    previous_playlist = ""
    current_playlist = ""

    def __init__(self):

        self.xmms = xmmsclient.XMMS("lwxc_playback")
        self.xmms_async = xmmsclient.XMMS("lwxc")

        try:
            self.xmms_async.connect(os.getenv("XMMS_PATH"), disconnect_func=self.disconnect)
        except IOError as detail:
            if config.get_autostart():
                subprocess.check_call("xmms2-launcher")
                # would like to use goto here
                self.xmms_async.connect(os.getenv("XMMS_PATH"), disconnect_func=self.disconnect)
            else:
                print("Connection failed:", detail)
                sys.exit(1)

        conn = GLibConnector(self.xmms_async)

        try:
            self.xmms.connect(os.getenv("XMMS_PATH"))
        except IOError as detail:
            print("Connection failed:", detail)
            sys.exit(1)

        self.current_track_elapsed = 0
        self.current_track_duration = 0
        self.current_pos = 0

        self.playback_cb = None

        self.channel = ''

    def play(self, widget):
        result = self.xmms.playback_start()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

    def pause(self, widget):
        result = self.xmms.playback_pause()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

    def stop(self, widget):
        result = self.xmms.playback_stop()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

    def next_(self, widget):
        result = self.xmms.playlist_set_next_rel(1)
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

        result = self.xmms.playback_tickle()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

    def prev(self, widget):
        result = self.xmms.playlist_set_next_rel(-1)
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

        result = self.xmms.playback_tickle()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

    def jump_to(self, pos):
        result = self.xmms.playlist_set_next(pos)
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

        result = self.xmms.playback_tickle()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())

        result = self.xmms.playback_start()
        result.wait()
        if result.iserror():
          print("Error:", result.get_error())


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
        # update previous playlist
        self.previous_playlist = self.current_playlist

        self.xmms_async.playlist_current_active(cb=self.got_current_playlist)

    def got_current_playlist(self, result):
        if result.is_error():
            print(result.value())
        else:
            # update current playlist
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

            playlists.sort()

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

                selection.select_path(path)

            else:
                selection.select_path(cur)
                view.scroll_to_cell(cur, None, True, 0.49, 0.0)

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

            # sanitize
            if current < 0:
                current = 0

            # playlist not empty
            if pos > 0:
                    # saved selection from current playlist
                    if self.current_playlist == self.previous_playlist:
                        # selection exists
                        if treeiter:
                            # selected track was deleted
                            if path.get_indices()[0] == pos:
                                path.prev()
                        else:
                            path = current
                    # no selection
                    else:
                        # select first track
                        path = current

                    # restore selection
                    selection.select_path(path)
                    # scroll to selection
                    view.scroll_to_cell(path, None, True, 0.49, 0.0)

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

    def setup_playlists_cb(self, func):
        # add/remove playlist
        self.xmms_async.broadcast_collection_changed(func)
        # switch playlist
        self.xmms_async.broadcast_playlist_loaded(func)

    def setup_playlist_cb(self, func):
        self.xmms_async.broadcast_playlist_changed(func)
        self.xmms_async.broadcast_playlist_current_pos(func)
        self.xmms_async.broadcast_playlist_loaded(func)

    def on_playlist_current_pos(self, position):
        if position.is_error():
            return

        self.current_pos = position.value()['position']

        status = self.xmms.playback_status()
        status.wait()
        if not status.is_error():
            if not status.value():
                # stopped
                self.xmms_async.playlist_list_entries(cb=self.on_playlist_current_pos_)

    def on_playlist_current_pos_(self, result):
        if result.is_error():
            return

        value = result.value()
        if not value:
            return

        mlib_id = value[self.current_pos]

        self.xmms_async.medialib_get_info(mlib_id, self.on_playlist_current_pos__)

    def on_playlist_current_pos__(self, result):
        if result.is_error():
            return
        self.current_track_elapsed = 0
        self.current_track_duration = result.value()['duration']
        self.playtime_cb(self.current_track_elapsed, self.current_track_duration)

    def on_playback_current_id(self, result):
        if result.is_error():
            return
        self.current_track_id = result.value()

        self.xmms_async.medialib_get_info(self.current_track_id, self.on_playback_current_id_)

    def on_playback_current_id_(self, result):
        if result.is_error():
            return
        self.current_track_duration = result.value()['duration']
        self.playtime_cb(self.current_track_elapsed, self.current_track_duration)
        
    def setup_playtime_cb(self, func):
        self.playtime_cb = func

        ## update elapsed
        self.xmms_async.signal_playback_playtime(self.on_playtime_cb)

        ## reset elapsed on stop
        self.xmms_async.broadcast_playback_status(self.on_playback_status)

        ## update duration
        # change while stopped
        self.xmms_async.broadcast_playlist_current_pos(self.on_playlist_current_pos)
        # change while playing
        self.xmms_async.broadcast_playback_current_id(self.on_playback_current_id)

        # set initial
        result = self.xmms.playback_playtime()
        result.wait()
        self.on_playtime_cb(result)
        result = self.xmms.playback_current_id()
        result.wait()
        self.on_playback_current_id(result)
        result = self.xmms.playlist_current_pos()
        result.wait()
        self.on_playlist_current_pos(result)

    def on_playback_status(self, result):
        if result.is_error():
            return
        value = result.value()

        if self.playback_cb:
            self.playback_cb(value)

    def setup_playback_cb(self, func):
        self.playback_cb = func

        # meh. no update for first request
        result = self.xmms.playback_status()
        result.wait()
        if result.is_error():
            return
        self.playback_cb(result.value())

    def on_playtime_cb(self, result):
        if result.is_error():
            return
        self.current_track_elapsed = result.value()

        self.playtime_cb(self.current_track_elapsed, self.current_track_duration)

    def seek(self, ms):
        result = self.xmms.playback_status()
        result.wait()
        if result.value() == xmmsclient.PLAYBACK_STATUS_PAUSE:
            self.xmms.playback_start()

        result = self.xmms.playback_seek_ms(ms)
        result.wait()

    def seek_forwards(self, offset):
        result = self.xmms.playback_playtime()
        result.wait()
        if result.is_error():
            return
        result = self.xmms.playback_status()
        result.wait()
        if result.value() == xmmsclient.PLAYBACK_STATUS_PAUSE:
            self.xmms.playback_start()

        result = self.xmms.playback_seek_ms(result.value() + offset)
        result.wait()

    def seek_backwards(self, offset):
        result = self.xmms.playback_playtime()
        result.wait()
        if result.is_error():
            return
        result = self.xmms.playback_status()
        result.wait()
        if result.value() == xmmsclient.PLAYBACK_STATUS_PAUSE:
            self.xmms.playback_start()

        result = self.xmms.playback_seek_ms(result.value() - offset)
        result.wait()

    def get_volume(self):
        result = self.xmms.playback_volume_get()
        result.wait()
        if result.is_error():
            return 100
        value = result.value()
        if not value:
            return 100
        self.channel, volume = list(value.items())[0]
        return volume

    def set_volume(self, vol):
        if not self.channel:
            return
        result = self.xmms.playback_volume_set(self.channel, vol)
        result.wait()

    def setup_volume_cb(self, func):
        self.volume_cb = func
        self.xmms_async.broadcast_playback_volume_changed(self.on_volume_cb)

    def on_volume_cb(self, result):
        if result.is_error():
            return
        value = result.value()
        if not value:
            # no pulseaudio stream
            return
        self.channel, volume = list(value.items())[0]
        self.volume_cb(volume)

    def remove_playlist(self, widget, name):
        if name != "":
            self.xmms_async.playlist_remove(name)

    def remove_playlist_entry(self, position):
        if position >= 0:
            self.xmms_async.playlist_remove_entry(position)

    def remove_playlist_entries(self, positions):
        for position in positions:
            self.xmms_async.playlist_remove_entry(position)

    def playlist_clear(self, widget, playlist):
        self.xmms_async.playlist_clear(playlist)

#    def playlist_remove(self, widget, playlist):
#        self.xmms_async.playlist_remove(playlist)

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
    force_show = "False"

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
            test.set("main", "FORCE_SHOW", self.force_show)
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
        try:
            self.force_show = parser.get("main", "FORCE_SHOW")
        except configparser.NoOptionError:
            parser.set("main", "FORCE_SHOW", self.force_show)
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

    def get_force_show(self):
        if self.force_show == "True":
            return True
        else:
            return False


def handle_sigterm(signum, frame):
    loop.quit()


class DBusService(dbus.service.Object):
    def __init__(self, instance):
        bus = dbus.SessionBus(mainloop=DBusGMainLoop())
        bus_name = dbus.service.BusName("org.example.lwxc." + instance, bus)
        dbus.service.Object.__init__(self, bus_name, "/org/example/lwxc")

    @dbus.service.method("org.example.lwxc")
    def show(self):
        window.toggle()
        return "done"


if __name__ == "__main__":
    global config
    global loop
    global connection
    global window
    global icon

    global iconname
    iconname = "/usr/share/pixmaps/lwxc.svg"

    config_home = os.getenv("XDG_CONFIG_HOME")

    if not config_home:
        config_home = os.path.expanduser("~/.config")

    config_path = config_home + "/xmms2/clients/lwxc/"

    parser = optparse.OptionParser()

    parser.add_option("-i", "--instance",
                      action="store", dest="instance", default="default",
                      help="name of instance")
    parser.add_option("-s", "--show",
                      action="store_true", dest="show", default=False,
                      help="show instance")

    (options, args) = parser.parse_args()


    if not os.path.exists(config_path):
        os.makedirs(config_path)


    try:
        config = Config(config_path + options.instance + ".conf")

        loop = GObject.MainLoop(None)

        connection = Connection()
        window = window_main(options.instance)
        icon = TrayIcon()

        if options.show:
            window.toggle()


        # check for running instance
        try:
            bus = dbus.SessionBus(mainloop=DBusGMainLoop())
            test_service = bus.get_object("org.example.lwxc." + options.instance, "/org/example/lwxc")
            test_method = test_service.get_dbus_method("show", "org.example.lwxc")
            result = test_method()
            if result == "done":
                sys.exit(0)
        except dbus.exceptions.DBusException:
            pass

        # register DBus Service
        service = DBusService(options.instance)


        # handle signals
        signal.signal(signal.SIGTERM, handle_sigterm)
        signal.signal(signal.SIGHUP, signal.SIG_IGN)

        loop.run()

    except KeyboardInterrupt:
        loop.quit()

    if config.get_autostop():
        connection.daemon_quit()

