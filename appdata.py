#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Licensed under the GNU General Public License Version 2
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# Copyright (C) 2013
#    Richard Hughes <richard@hughsie.com>
#

#import os
import sys
import re
import xml.etree.ElementTree as ET

XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'

class AppData:

    def __init__(self):
        self.root = None
        self.filename = None

    def extract(self, filename):
        try:
            tree = ET.parse(filename)
        except ET.ParseError, e:
            return False
        self.root = tree.getroot()
        self.filename = filename
        return True

    def get_id(self):
        tmp = self.root.find("id").text
        if tmp:
            tmp = tmp.replace('.desktop', '')
        return tmp
    def get_licence(self):
        tmp = self.root.find("licence").text
        if tmp == 'CC BY':
            tmp = u'CC-BY'
        elif tmp == 'CC BY-SA':
            tmp = u'CC-BY-SA'
        return tmp
    def get_screenshots(self):
        values = []
        ss = self.root.find("screenshots")
        if ss is None:
            return values
        for item in ss:
            if item.tag != 'screenshot':
                continue
            values.append(item.text)
        return values
    def get_metadata(self):
        values = {}
        ss = self.root.find("metadata")
        if ss is None:
            return values
        for item in ss:
            if item.tag != 'value':
                continue
            if isinstance(item.text, unicode):
                values[item.get('key')] = item.text
            else:
                values[item.get('key')] = item.text.decode('utf-8')
        return values

    def get_compulsory_for_desktop(self):
        values = []
        for item in self.root:
            if item.tag == 'compulsory_for_desktop':
                values.append(item.text)
        return values
    def _append_for_lang(self, descriptions, lang, content):
        if not lang:
            lang = u'C'

        if lang in descriptions:
            descriptions[lang] = descriptions[lang] + content
        else:
            descriptions[lang] = content

    def get_descriptions(self):
        descriptions = {}
        ss = self.root.find("description")
        if ss is None:
            return
        for item in ss:
            if item.tag == 'p':
                para = item.text
                para = para.lstrip()
                para = para.replace('\n', ' ')
                para = re.sub('\ +', ' ', para)
                self._append_for_lang(descriptions, item.get(XML_LANG), para + u'\n\n')
            elif item.tag == 'ul':
                for li in item:
                    txt = li.text
                    txt = txt.replace('\n', ' ')
                    txt = re.sub('\ +', ' ', txt)
                    self._append_for_lang(descriptions, item.get(XML_LANG), u' • ' + txt + u'\n')
            elif item.tag == 'ol':
                cnt = 1
                for li in item:
                    txt = li.text
                    txt = txt.replace('\n', ' ')
                    txt = re.sub('\ +', ' ', txt)
                    self._append_for_lang(descriptions, item.get(XML_LANG), u' ' + str(cnt) + u'. ' + txt + u'\n')
                    cnt = cnt + 1
            else:
                raise StandardError('Do not know how to parse' + item.tag + ' for ' + self.filename)

        for lang in descriptions:
            descriptions[lang] = descriptions[lang].replace('  ', ' ').rstrip()
        return descriptions

    def get_urls(self):
        values = {}
        for item in self.root:
            if item.tag == 'url':
                key = item.get('type')
                values[key] = item.text
        return values

    def get_project_group(self):
        ss = self.root.find("project_group")
        if ss is not None:
            return ss.text

    def _get_localized_tags(self, name):
        values = {}
        for item in self.root:
            if item.tag == name:
                lang = item.get(XML_LANG)
                if not lang:
                    lang = 'C'
                if isinstance(item.text, unicode):
                    values[lang] = item.text
                else:
                    values[lang] = item.text.decode('utf-8')
        if len(values) == 0:
            return None
        return values

    def get_names(self):
        return self._get_localized_tags('name')

    def get_summaries(self):
        return self._get_localized_tags('summary')

def main():
    data = AppData()
    data.extract(sys.argv[1])
    print 'id:\t\t', data.get_id()
    print 'licence:\t', data.get_licence()
    print 'urls:\t\t', data.get_urls()
    print 'project_group:\t\t', data.get_project_group()
    print 'screenshots:\t\t', data.get_screenshots()
    print 'description:\t', data.get_descriptions()
    print 'END'
    sys.exit(0)

if __name__ == "__main__":
    main()
