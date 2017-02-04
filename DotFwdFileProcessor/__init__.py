# -*- coding: utf-8 -*-
"""
/***************************************************************************
 DotFwdFileProcessor
                                 A QGIS plugin
 This plugin processes .fwd files to polyline for web mapping use
                             -------------------
        begin                : 2017-01-05
        copyright            : (C) 2017 by Eric Kabuchanga | SeniorDeveloper | KEGeoS Solutions Limited
        email                : kabuchanga@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load DotFwdFileProcessor class from file DotFwdFileProcessor.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Dot_Fwd_File_Processor import DotFwdFileProcessor
    return DotFwdFileProcessor(iface)
