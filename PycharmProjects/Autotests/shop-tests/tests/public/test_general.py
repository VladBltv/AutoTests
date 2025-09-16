from befree.api_model import api
import allure
from allure_commons.types import Severity
from pytest_check import check
import os
from dotenv import load_dotenv

load_dotenv()

public_host_url = os.getenv("SHOP_URL")


@allure.id("1523")
@allure.title("Линки на приложение в сторах")
@allure.description("Проверяем, что установлены корректные ссылки на приложения в appstore и google play")
@allure.tag("UI Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Common")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.feature("Footer")
def test_verify_stores_link():
    with allure.step("Получить код главной страницы"):
        response_main = api.front_session.get("/zhenskaya")

    with allure.step(
        "Проверить что для google play установлена ссылка https://play.google.com/store/apps/details?id=com.ddgcorp.befree"
    ):
        assert "https://play.google.com/store/apps/details?id=com.ddgcorp.befree" in response_main.text

    with allure.step("Проверить что для appstore установлена ссылка https://apps.apple.com/ru/app/befree/id1040073468"):
        assert "https://apps.apple.com/ru/app/befree/id1040073468" in response_main.text


@allure.id("2712")
@allure.title("Принудительные редиректы со страниц каталога")
@allure.tag("UI Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Listing")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.feature("Редирект")
def test_308_redirects():
    from_list = [
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=9",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=2",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=3",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=4",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=5",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=6",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=7",
        "/zhenskaya/zen-odezda/zen-niznee-bele?page=5",
        "/zhenskaya/zen-odezda/noski-i-kolgotki?page=5",
        "/zhenskaya/odezhda/legginsy",
        "/muzhskaya/muz-odezda/muz-futbolki-i-longslivy",
        "/zhenskaya/odezhda/bluzki-i-rubashki/bluzki?page=2",
        "/zhenskaya/odezhda/bluzki-i-rubashki/bluzki",
        "/zhenskaya/zen-aksessuary/zen-riukzaki-i-sumki",
        "/muzhskaya/muz-odezda/muz-tolstovki-i-xudi",
        "/zhenskaya/zen-odezda/bluzki-i-rubaski",
        "/muzhskaya/muz-aksessuary/muz-golovnye-ubory",
        "/zhenskaya/zen-odezda/briuki-i-legginsy",
        "/zhenskaya/pidzaki-i-zakety-zenskie",
        "/zhenskaya/kombinezony-zenskie",
        "/zhenskaya/bodi-1",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=20",
        "/zhenskaya/zen-odezda/zen-svitery-i-kardigany?page=6",
        "/zhenskaya/zen-odezda/pidzaki-i-zakety?page=2",
        "/zhenskaya/zen-odezda/briuki-i-legginsy?page=5",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=6",
        "/zhenskaya/zen-odezda/zen-verxniaia-odezda?page=5",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=22",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=13",
        "/zhenskaya/zen-odezda/pidzaki-i-zakety",
        "/zhenskaya/zen-odezda/zen-sportivnaia-odezda",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=8",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=11",
        "/zhenskaya/zen-odezda/zen-verxniaia-odezda?page=3",
        "/zhenskaya/zen-odezda/zen-verxniaia-odezda?page=3",
        "/zhenskaya/zen-odezda/zen-futbolki-i-polo?page=12",
    ]

    to_list = [
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/zen-niznee-bele",
        "/zhenskaya/noski-i-kolgotki",
        "/zhenskaya/legginsy",
        "/muzhskaya/muz-futbolki-i-longslivy",
        "/zhenskaya/bluzki",
        "/zhenskaya/bluzki",
        "/zhenskaya/zen-riukzaki-i-sumki",
        "/muzhskaya/muz-tolstovki-i-xudi",
        "/zhenskaya/bluzki-i-rubaski",
        "/muzhskaya/muz-golovnye-ubory",
        "/zhenskaya/briuki-i-legginsy",
        "/zhenskaya/pidzaki-i-zakety",
        "/zhenskaya/zen-kombinezony",
        "/zhenskaya/bluzki-bodi",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/zen-svitery-i-kardigany",
        "/zhenskaya/pidzaki-i-zakety",
        "/zhenskaya/briuki-i-legginsy",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/zen-verxniaia-odezda",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/pidzaki-i-zakety",
        "/zhenskaya/zen-sportivnaia-odezda",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/zen-futbolki-i-polo",
        "/zhenskaya/zen-verxniaia-odezda",
        "/zhenskaya/zen-verxniaia-odezda",
        "/zhenskaya/zen-futbolki-i-polo",
    ]

    for i in range(len(from_list)):
        with allure.step(f"Запросить страницу с которой нужно сделать редирект {from_list[i]}"):
            response = api.front_session.get(f"{from_list[i]}")
        with allure.step("Проверить, что сработал редирект 308"):
            assert response.history[0].status_code == 308
        with allure.step(f"Проверить, что урл на который произошел редирект соответствует {to_list[i]}"):
            parts = response.url.split("/")
            url = f"/{parts[-2]}/{parts[-1]}"
            assert url == f"{to_list[i]}", f"{i}"


@allure.id("2967")
@allure.title("Редиректы со страниц товаров")
@allure.tag("UI Test")
@allure.severity(Severity.CRITICAL)
@allure.suite("Product")
@allure.label("owner", "Potegova")
@allure.label("service", "Public")
@allure.feature("Редирект")
def test_product_redirects():
    with allure.step("Со страниц с символом $ в артикуле идет редирект на страницу товара без доллара в артикуле"):
        with allure.step("Перейти на страницу товара с символом $ в артикуле"):
            response = api.front_session.get("/zhenskaya/product/2231549733$D/50")

        with allure.step("Проверить, что произошел редирект на страницу товара без $ в артикуле"):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/2231549733/50")

    with allure.step("Со страниц с определнным размером идет редирект на страницу без этого размера"):
        with allure.step("Задаем массив с размерами"):
            sizes = [
                516,517,518,519,520,521,522,523,524,525,526,527,528,529,530,531,532,533,534,535,536,537,538,539,540,541,
                542,543,544,545,546,547,548,549,550,551,552,553,554,555,556,557,558,559,560,561,562,563,564,565,566,567,
                568,569,570,571,572,573,574,575,576,577,578,579,580,581,582,583,584,585,586,587,588,589,590,591,592,593,
                594,595,596,597,598,599,600,601,602,603,604,605,606,607,608,609,610,611,612,613,614,615,616,617,618,619,
                620,621,622,623,624,625,626,627,628,629,630,631,632,633,634,635,636,637,638,639,640,641,642,643,644,645,
                646,647,648,649,650,651,652,653,654,655,656,657,658,659,660,661,662,663,664,665,666,667,668,669,670,671,
                672,673,674,675,676,677,678,679,680,681,682,683,684,685,686,687,688,689,690,691,692,693,694,695,696,697,
                698,699,700,701,702,703,704,705,706,707,708,709,710,711,712,713,714,715,716,717,718,719,720,721,722,723,
                724,725,726,727,728,729,730,731,732,733,734,735,736,737,738,739,740,741,742,743,744,745,746,747,748,749,
                750,751,752,753,754,755,756,757,758,759,760,761,762,763,764,765,766,767,768,769,770,771,772,773,774,775,
                776,777,778,779,780,781,782,783,784,785,786,787,788,789,790,791,792,793,794,795,796,797,798,799,800,801,
                802,803,804,805,806,807,808,809,810,811,812,813,814,815,816,817,818,819,820,821,822,823,824,825,826,827,
                828,829,830,831,832,833,834,835,836,837,838,839,840,841,842,843,844,845,846,847,848,849,850,851,852,853,
                854,855,856,857,858,859,860,861,862,863,864,865,866,867,868,869,870,871,872,873,874,875,876,877,878,879,
                880,881,882,883,884,885,886,887,888,889,890,891,892,893,894,895,896,897,898,899,900,901,902,903,904,905,
                906,907,908,909,910,911,912,913,914,915,916,917,918,919,920,921,922,923,924,925,926,927,928,929,930,931,
                932,933,934,935,936,937,938,939,940,941,942,943,944,945,946,947,948,949,950,951,952,953,954,955,956,957,
                958,959,960,961,962,963,964,965,966,967,968,969,970,971,972,973,974,975,976,977,978,979,980,981,982,983,
                984,985,986,987,988,989,990,991,992,993,994,995,996,997,998,999,1000,1001,1002,1003,1004,1005,1006,1007,
                1008,1009,1010,1011,1012,1013,1014,1015,1016,1017,1018,1019,1020,1021,1022,1023,1024,1025,1026,1027,1028,
                1029,1030,1031,1032,1033,1034,1035,1036,1037,1038,1039,1040,1041,1042,1043,1044,1045,1046,1047,1048,1049,
                1050,1051,1052,1053,1054,1055,1056,1057,1058,1059,1060,1061,1062,1063,1064,1065,1066,1067,1068,1069,1070,
                1071,1072,1073,1074,1075,1076,1077,1078,1079,1080,1081,1082,1083,1084,1085,1086,1087,1088,1089,1090,1091,
                1092,1093,1094,1095,1096,1097,1098,1099,1100,1101,1102,1103,1104,1105,1106,1107,1108,1109,1110,1111,1112,
                1113,1114,1115,1116,1117,1118,1119,1120,1121,1122,1123,1124,1125,1126,1127,1128,1129,1130,1131,1132,1133,
                1134,1135,1136,1137,1138,1139,1140,1141,1142,1143,1144,1145,1146,1147,1148,1149,1150,1151,1152,1153,1154,
                1155,1156,1157,1158,1159,1160,1161,1162,1163,1164,1165,1166,1167,1168,1169,1170,1171,1172,1173,1174,1175,
                1176,1177,1178,1179,1180,1181,1182,1183,1184,1185,1186,1187,1188,1189,1190,1191,1192,1193,1194,1195,1196,
                1197,1198,1199,1200,1201,1202,1203,1204,1205,1206,1207,1208,1209,1210,1211,1212,1213,1214,1215,1216,1217,
                1218,1219,1220,1221,1222,1223,1224,1225,1226,1227,1228,1229,1230,1231,1232,1233,1234,1235,1236,1237,1238,
                1239,1240,1241,1242,1243,1244,1245,1246,1247,1248,1249,1250,1251,1252,1253,1254,1255,1256,1257,1258,1259,
                1260,1261,1262,1263,1264,1265,1266,1267,1268,1269,1270,1271,1272,1273,1274,1275,1276,1277,1278,1279,1280,
                1281,1282,1283,1284,1285,1286,1287,1288,1289,1290,1291,1292,1293,1294,1295,1296,1297,1298,1299,1300,1301,
                1302,1303,1304,1305,1306,1307,1308,1309,1310,1311,1312,1313,1314,1315,1316,1317,1318,1319,1320,1321,1322,
                1323,1324,1325,1326,1327,1328,1329,1330,1331,1332,1333,1334,1335,1336,1337,1338,1339,1340,1341,1342,1343,
                1344,1345,1346,1347,1348,1349,1350,1351,1352,1353,1354,1355,1356,1357,1358,1359,1360,1361,1362,1363,1364,
                1365,1366,1367,1368,1369,1370,1371,1372,1373,1374,1375,1376,1377,1378,1379,1380,1381,1382,1383,1384,1385,
                1386,1387,1388,1389,1390,1391,1392,1393,1394,1395,1396,1397,1398,1399,1400,1401,1402,1403,1404,1405,1406,
                1407,1408,1409,1410,1411,1412,1413,1414
            ]

        for i in range(len(sizes)):
            with allure.step(f"Запросить страницу товара с размером {sizes[i]}"):
                response = api.front_session.get(f"/zhenskaya/product/BF2531209063/106?size={sizes[i]}")

            with allure.step("Проверить, что произошел редирект на страницу товара без переданного размера"):
                try:
                    check.equal(response.history[0].status_code, 308)
                except IndexError:
                    print(f"Ошибка IndexError: нет редиректа для размера {sizes[i]}")
                    print(f"response.status_code: {response.status_code}")
                except Exception as e:
                    print(f"Неожиданная ошибка для размера {sizes[i]}: {e}")

                check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/BF2531209063/106")

    with allure.step("При запросе товара с неверным гендером происходит редирект на страницу товара с верным гендером"):
        with allure.step("Запросить товар с женским гендером под мужским"):
            response = api.front_session.get("/muzhskaya/product/BF2531414033/50")

        with allure.step("Проверить, что произошел редирект на страницу товара с женским гендером"):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/BF2531414033/50")

        with allure.step("Запросить товар с мужским гендером под женским"):
            response = api.front_session.get("/zhenskaya/product/BF2523109021/107")

        with allure.step("Проверить, что произошел редирект на страницу товара с мужским гендером"):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.url.replace(public_host_url, ""), "/muzhskaya/product/BF2523109021/107")

    with allure.step("Редиректы при комбинации условий."):
        with allure.step("Запросить товар с женским гендером под мужским с $ в артикуле"):
            response = api.front_session.get("/muzhskaya/product/BF2531414033$D/50")

        with allure.step("Произошел редирект на страницу товара с женским гендером, в артикуле нет $"):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.history[1].status_code, 308)
            check.equal(len(response.history), 2)
            check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/BF2531414033/50")

        with allure.step("Запросить товар с мужским гендером под женским и размером 516"):
            response = api.front_session.get("/zhenskaya/product/BF2523109021/107?size=516")

        with allure.step(
            "Происходит два редиректа. Произошел редирект на страницу товара с мужским гендером, в урле нет размера 516"
        ):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.history[1].status_code, 308)
            check.equal(len(response.history), 2)
            check.equal(response.url.replace(public_host_url, ""), "/muzhskaya/product/BF2523109021/107")

        with allure.step("Запросить товар с $ в артикуле и размером из монолита"):
            response = api.front_session.get("/zhenskaya/product/BF2531414033$D/50?size=516")

        with allure.step(
                "Происходит один редирект. Произошел редирект на страницу товара где в артикуле нет $, в урле нет размера 516"
        ):
            check.equal(response.history[0].status_code, 308)
            check.equal(len(response.history), 1)
            check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/BF2531414033/50")

        with allure.step("Запросить товар с $ в артикуле и размером из монолита, под неверным гендером"):
            response = api.front_session.get("/muzhskaya/product/BF2531414033$D/50?size=516")

        with allure.step(
                "Происходит два редиректа. Произошел редирект на страницу товара где в артикуле нет $, в урле нет размера 516, верный гендер"
        ):
            check.equal(response.history[0].status_code, 308)
            check.equal(response.history[0].status_code, 308)
            check.equal(len(response.history), 2)
            check.equal(response.url.replace(public_host_url, ""), "/zhenskaya/product/BF2531414033/50")
