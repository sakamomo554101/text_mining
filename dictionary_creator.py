import csv
import re

keyword_file_names = {"wikipedia": "jawiki-latest-all-titles-in-ns0", "hatena": "keywordlist_furigana.csv"}


def main():
    # create csv
    with open("custom_dict.csv", "w") as csv_file:
        for type, filename in keyword_file_names.items():
            with open(filename, "r") as keyword_file:
                list = keyword_file.readlines()

                # debug print
                print("{} : keyword count is {}".format(filename, len(list)))

                # keywordを取得して、不要な語を削除して、登録
                exclude_patterns = [
                    "%r(^[+-.$()?*/&%!\"'_,]+)",
                    "/^[-.0-9]+$/",
                    "/曖昧さ回避/",
                    "/_\(/",
                    "/^PJ:/",
                    "/の登場人物/",
                    "/一覧/"
                ]
                for keyword in list:
                    # 不要な空白を削除
                    keyword = keyword.strip()

                    # 除外リストに含まれるかをチェックする
                    can_add_title = True
                    for exclude_pattern in exclude_patterns:
                        result = re.compile(exclude_pattern).match(keyword)
                        if result is not None:
                            can_add_title = False
                            break

                    # 除外リストがヒットした場合は、対象となるタイトルはcsvに追加しない
                    if not can_add_title:
                        continue

                    # タイトルの長さが3文字未満の場合は追加しない
                    length = len(keyword)
                    if length < 3:
                        continue

                    # 辞書に登録するためにスコアを計算し、登録する
                    score = max(-36000.0, -400 * (length ** 1.5))
                    row = [keyword, None, None, score, '名詞', '一般', '*', '*', '*', '*', keyword, '*', '*', type]

                    print("add keyword : {}, score is {}".format(keyword, str(score)))
                    writer = csv.writer(csv_file, lineterminator='\n')
                    writer.writerow(row)


if __name__ == "__main__":
    print("start : create user dictionary csv for mecab.")
    main()
