import Image_comparation as comp

# не то сравниваю, нужно сжатую - сжатую с ошибками, несжатуу - несжатую с ошибками .... Это сделано, но криво...
# TODO сделать красиво
orig_file_list = ["AMDTest/no_errors_b4.bmp", "Berlin/no_errors_b4.bmp", "Gladiolus/no_errors_b4.bmp"]
folders_list = ["\AMDTest", "\Berlin", "\Gladiolus"]

comp.do_comparation(orig_file_list, folders_list)

# first lab #########################################################################
# m.WriteToFile("\Berlin_4", m.calcContrast, m.calc_RMS_Contrast, m.calc_CustomMetric, m.calc_CustomMetric_a,
#               m.calc_CustomMetric_b)
# m.WriteToFile("\AmdTest_4", m.calcContrast, m.calc_RMS_Contrast, m.calc_CustomMetric, m.calc_CustomMetric_a,
#               m.calc_CustomMetric_b)
# m.WriteToFile("\Gladiolus_4", m.calcContrast, m.calc_RMS_Contrast, m.calc_CustomMetric, m.calc_CustomMetric_a,
#               m.calc_CustomMetric_b)
