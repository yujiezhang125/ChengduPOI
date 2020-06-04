# -*- coding: utf-8 -*-
# @Time    : 2020/05/14
# @Author  : yujiezhang125
# @FileName: chengdupoi.py
# @Description: Reclassify chengdu raster data to grassland, bareland, cropland and built-up area(four land-use type).
# @Description: Calculate the area of each land-use type in 3km*3km poi
# @Description: And calculate the nearest distance to airport, CBD etc.


import arcpy
from arcpy.sa import *
import os
import time

arcpy.env.workspace = r'D:\CityDNA\Data\chengdupoi\chengduWGS84\chegdu.gdb'
arcpy.env.overwriteOutput = True

dir_root = r'D:\CityDNA\Data\chengdupoi'
os.chdir(dir_root)
os.path.join(dir_root, 'data0511\\poiCat.gdb\\', 'transit')
chengdu3 = 'chengdu3km'


joinfields = ['transit', 'restaurant', 'office', 'mall', 'hotel', 'education', 'bank', 'recreation', 'touristic', 'pop']
for fld in joinfields:
    print fld + " start..."
    target_features = chengdu3
    join_features = os.path.join(dir_root, 'data0511\\poiCat.gdb\\', fld)
    out_feature_class = chengdu3 + '_' + fld

    # 面join点得到面文件
    print fld + " spatial join..."
    arcpy.SpatialJoin_analysis(target_features, join_features, out_feature_class)
    print fld + " alter field name..."
    arcpy.AlterField_management(out_feature_class, 'Join_Count', fld)
    chengdu3 = chengdu3 + '_' + fld
    print fld + " finished!"


keepfields = ['OBJECTID', 'FID', 'Shape', 'Id', 'Shape_Length', 'Shape_Area', 'transit', 'restaurant', 'office', 'mall', 'hotel', 'education', 'bank', 'recreation', 'touristic', 'pop']
chengdu3 = 'chengdu3km'
names = arcpy.ListFields('chengdu3km_transit_restaurant_office_mall_hotel_education_bank_recreation_touristic_pop')
dropfields = []
for i in range(len(names)):
    if names[i].name not in keepfields:
        dropfields.append(names[i].name)

arcpy.MakeFeatureLayer_management('chengdu3km_transit_restaurant_office_mall_hotel_education_bank_recreation_touristic_pop', 'lyr')
arcpy.CopyFeatures_management('lyr', chengdu3 + '_pnt')
arcpy.Delete_management('lyr')
arcpy.DeleteField_management(chengdu3 + '_pnt', dropfields)


# spatial join point files finished====================================================================================
# raster files
arcpy.CheckOutExtension("Spatial")
arcpy.env.workspace = r"D:\CityDNA\Data\chengdupoi\raster"
arcpy.env.overwriteOutput = True

# reclassify cropland!!
print "crop.tif reclassify..."
outReclass = Reclassify("chengdu.tif", "Value", RemapRange([[0, 9, 0], [10, 1], [11, 130, 0]]))
print "crop.tif reclassify finished..."
time.sleep(20)
outReclass.save(r"D:\CityDNA\Data\chengdupoi\raster\\" + "cropland_RCLS.tif")
time.sleep(5)
del outReclass
print "crop.tif Finished!"

# reclassify grassland!!
print "grs.tif reclassify..."
outReclass = Reclassify("chengdu.tif", "Value", RemapRange([[0, 29, 0], [30, 1], [31, 130, 0]]))
print "grs.tif reclassify finished..."
time.sleep(20)
outReclass.save(r"D:\CityDNA\Data\chengdupoi\raster\\" + "grassland_RCLS.tif")
time.sleep(5)
del outReclass
print "grs.tif Finished!"

# reclassify city_county!!
print "ct.tif reclassify..."
time.sleep(20)
outReclass = Reclassify("chengdu.tif", "Value", RemapRange([[0, 79, 0], [80, 1], [81, 130, 0]]))
print "ct.tif reclassify finished..."

outReclass.save(r"D:\CityDNA\Data\chengdupoi\raster\\" + "city_county_RCLS.tif")
time.sleep(5)
del outReclass
print "ct.tif Finished!"

# reclassify bareland!!
print "bl.tif reclassify..."
time.sleep(20)
outReclass = Reclassify("chengdu.tif", "Value", RemapRange([[0, 89, 0], [90, 1], [91, 130, 0]]))
print "bl.tif reclassify finished..."

outReclass.save(r"D:\CityDNA\Data\chengdupoi\raster\\" + "bareland_RCLS.tif")
time.sleep(5)
del outReclass
print "bl.tif Finished!"


# calulate area of each land-use type
in_zone_path = r'D:\CityDNA\Data\chengdupoi\chengduWGS84\chegdu.gdb\\'
zone_field = "CODE"
in_raster_path = r"D:\CityDNA\Data\chengdupoi\raster\\"
out_cityarea_path = r"D:\CityDNA\Data\tiffdata\cityarea.gdb\\"
out_table_path = r"D:\CityDNA\Data\chengdupoi\chengduWGS84\chegdu.gdb\\"
# cropland
print " zonal statistics..."
outZSaT = ZonalStatisticsAsTable(in_zone_path + "chengdu3km", "FID",
                                in_raster_path + "cropland_RCLS.tif",
                                out_table_path + "cropland_tb", "NODATA", "SUM")
print " add percent field..."
arcpy.AddField_management(out_table_path + "cropland_tb", "cropland", "DOUBLE")
print " calculate percent..."
arcpy.CalculateField_management(out_table_path + "cropland_tb", "cropland", '!SUM! * 9.5 * 9.5', "PYTHON_9.3")

# grassland
print " zonal statistics..."
outZSaT = ZonalStatisticsAsTable(in_zone_path + "chengdu3km", "FID",
                                in_raster_path + "grassland_RCLS.tif",
                                out_table_path + "grassland_tb", "NODATA", "SUM")
print " add percent field..."
arcpy.AddField_management(out_table_path + "grassland_tb", "grassland", "DOUBLE")
print " calculate percent..."
arcpy.CalculateField_management(out_table_path + "grassland_tb", "grassland", '!SUM! * 9.5 * 9.5', "PYTHON_9.3")

# city_county
print " zonal statistics..."
outZSaT = ZonalStatisticsAsTable(in_zone_path + "chengdu3km", "FID",
                                in_raster_path + "city_county_RCLS.tif",
                                out_table_path + "city_county_tb", "NODATA", "SUM")
print " add percent field..."
arcpy.AddField_management(out_table_path + "city_county_tb", "city_county", "DOUBLE")
print " calculate percent..."
arcpy.CalculateField_management(out_table_path + "city_county_tb", "city_county", '!SUM! * 9.5 * 9.5', "PYTHON_9.3")

# bareland
print " zonal statistics..."
outZSaT = ZonalStatisticsAsTable(in_zone_path + "chengdu3km", "FID",
                                in_raster_path + "bareland_RCLS.tif",
                                out_table_path + "bareland_tb", "NODATA", "SUM")
print " add percent field..."
arcpy.AddField_management(out_table_path + "bareland_tb", "bareland", "DOUBLE")
print " calculate percent..."
arcpy.CalculateField_management(out_table_path + "bareland_tb", "bareland", '!SUM! * 9.5 * 9.5', "PYTHON_9.3")


#  add join
arcpy.env.workspace = r'D:\CityDNA\Data\chengdupoi\chengduWGS84\chegdu.gdb'
arcpy.env.overwriteOutput = True

keepfields = ['OBJECTID', 'FID', 'Shape', 'Id', 'Shape_Length', 'Shape_Area', 'cropland', 'grassland', 'city_county', 'bareland']
chengdu3 = 'chengdu3km'
names = arcpy.ListFields(out_table_path + chengdu3 + "_land")
dropfields = []
for i in range(len(names)):
    if names[i].name not in keepfields:
        dropfields.append(names[i].name)

arcpy.MakeFeatureLayer_management(out_table_path + chengdu3 + "_land", 'lyr')
arcpy.CopyFeatures_management('lyr', chengdu3 + '_landfinal')
arcpy.Delete_management('lyr')
arcpy.DeleteField_management(chengdu3 + '_landfinal', dropfields)

# calculate area finished =====================================================================================
# calculate nearest distance
arcpy.Near_analysis('chengdu3', os.path.join(dir_root, 'data0511\\poiCat.gdb\\', 'airport'))
arcpy.AlterField_management('chengdu3', 'Near_Dist', 'airport')

arcpy.Near_analysis('chengdu3', os.path.join(dir_root, 'data0511\\poiCat.gdb\\', 'port'))
arcpy.AlterField_management('chengdu3', 'Near_Dist', 'port')

arcpy.Near_analysis('chengdu3', os.path.join(dir_root, 'data0511\\poiCat.gdb\\', 'logistic'))
arcpy.AlterField_management('chengdu3', 'Near_Dist', 'logistic')

arcpy.Near_analysis('chengdu3km_distnew', os.path.join(dir_root, 'data0511\\poiCat.gdb\\', 'CBD_polygon'))
arcpy.AlterField_management('chengdu3km_distnew', 'Near_Dist', 'CBD')

arcpy.DeleteField_management('chengdu3', 'NEAR_FID')
