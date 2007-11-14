# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Generic reader class
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import Wammu.Thread
import Wammu
if Wammu.gammu_error == None:
    import gammu

class Reader(Wammu.Thread.Thread):
    '''
    Generic thread for reading information from phone.
    '''
    def FallBackStatus(self):
        '''
        Returns fall back status if real can not be obtained.
        '''
        return 200

    def GetNextStart(self):
        '''
        Initiates get next sequence.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def GetNext(self, location):
        '''
        Gets next entry.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def Get(self, location):
        '''
        Gets entry.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def GetStatus(self):
        '''
        Gets status of entries.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def Parse(self):
        '''
        Parses entry.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def Send(self):
        '''
        Sends entries to parent.

        Should be implemented in subclases.
        '''
        raise Exception('Not implemented!')

    def Run(self):
        '''
        Main reader function, executed in thread.
        '''
        self.ShowProgress(0)

        guess = False
        try:
            total = self.GetStatus()
        except gammu.GSMError, val:
            guess = True
            total = self.FallBackStatus()

        remain = total

        data = []

        try:
            start = True
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    if start:
                        value = self.GetNextStart()
                        start = False
                    else:
                        try:
                            loc = value['Location']
                        except TypeError:
                            loc = value[0]['Location']
                        value = self.GetNext(loc)
                except gammu.ERR_CORRUPTED:
                    self.ShowMessage(
                            _('Ignoring corrupted'),
                            _('While reading, entry on location %d seems to be corrupted, ignoring it!') % loc)
                    continue
                except gammu.ERR_EMPTY:
                    break

                self.Parse(value)
                if type(value) == list:
                    for i in range(len(value)):
                        value[i]['Synced'] = True
                else:
                    value['Synced'] = True
                data.append(value)
                remain = remain - 1
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            location = 1
            empty = 0
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    value = self.Get(location)
                    self.Parse(value)
                    if type(value) == list:
                        for i in range(len(value)):
                            value[i]['Synced'] = True
                    else:
                        value['Synced'] = True
                    data.append(value)
                    remain = remain - 1
                    # If we didn't know count and reached end, try some more entries
                    if remain == 0 and guess:
                        remain = 20
                        total = total + 20
                    empty = 0
                except gammu.ERR_EMPTY, val:
                    empty = empty + 1
                    # If we didn't know count and saw many empty entries, stop right now
                    if empty >= 50 and guess:
                        break
                    # If we didn't read anything for long time, we bail out (workaround bad count reported by phone)
                    if empty >= 70 and remain < 10:
                        self.ShowError(val[0])
                        remain = 0
                except gammu.ERR_CORRUPTED:
                    self.ShowMessage(
                            _('Ignoring corrupted'),
                            _('While reading, entry on location %d seems to be corrupted, ignoring it!') % location)
                    continue
                except gammu.GSMError, val:
                    self.ShowError(val[0], True)
                    return
                location = location + 1
        except gammu.ERR_INVALIDLOCATION:
            # if we reached end with guess, it is okay
            if not guess:
                self.ShowError(val[0], True)
                return
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

        self.Send(data)
