import pandas as pd
import itertools


class WordDatabase:
    def __init__(self):
        self.__one_word_count_frame = pd.DataFrame(
            columns=["word", "count"]
        )
        self.__couple_words_count_frame = pd.DataFrame(
            columns=[
                "word1",
                "word2",
                "count1",
                "count2",
                "intersection_count",  # 積集合
                "union_count",         # 和集合
                "jaccard_coefficient"  # jaccard係数（共起ネットワークでの重み）
            ]
        )

    def register_word_list(self, word_list):
        # 単語の出現数を登録
        self.countup_word_list(word_list)

        # 共起単語（2単語のペア）の出現数を登録
        word_list = list(set(word_list))  # 重複除外のため、一度setに変換している
        combination_word_pairs = list(itertools.combinations(word_list, 2))
        for combination_word_pair in combination_word_pairs:
            self.countup_couple_words(
                combination_word_pair[0],
                combination_word_pair[1]
            )

        # jaccard係数をアップデート
        self.update_jaccard_coefficient()

    def countup_word_list(self, word_list):
        # 複数単語を登録する
        for word in word_list:
            self.countup_one_word(word)

    def countup_one_word(self, word):
        db = self.__one_word_count_frame
        extract_frame = db[db["word"] == word]

        row_num = len(extract_frame)
        if row_num == 0:
            # 行数が0の場合は新規追加
            s = pd.Series([word, 1], index=db.columns)
            self.__one_word_count_frame = db.append(s, ignore_index=True)
        elif row_num == 1:
            # すでに追加されている場合はcountを+1する
            db.loc[db["word"] == word, "count"] = db.loc[db["word"] == word, "count"] + 1
        else:
            # 重複した単語がある場合は例外対応（TODO）
            print("{} is duplicated!".format(word))

    def countup_couple_words(self, word1, word2):
        db = self.__couple_words_count_frame
        extract_frame = db[(db["word1"] == word1) & (db["word2"] == word2)]

        row_num = len(extract_frame)
        if row_num == 0:
            # 行数が0の場合は新規追加
            s = pd.Series(
                [word1, word2, 0, 0, 1, 0, 0],
                index=db.columns
            )
            self.__couple_words_count_frame = db.append(s, ignore_index=True)
        elif row_num == 1:
            # すでに追加されている場合はcountを+1する
            # TODO : もうちょっと良い感じに書けないだろうか・・
            db.loc[(db["word1"] == word1) & (db["word2"] == word2), "intersection_count"] \
                = db.loc[(db["word1"] == word1) & (db["word2"] == word2), "intersection_count"] + 1
        else:
            # 重複した単語がある場合は例外対応（TODO）
            print("{}/{} is duplicated!".format(word1, word2))

    def update_jaccard_coefficient(self):
        # 全ての共起単語のjaccard係数をアップデートする
        def update_one_jaccard_coefficient(row):
            db = self.__one_word_count_frame

            # 単語数の更新
            row["count1"] = db.at[db[db["word"] == row["word1"]].index[0], "count"]
            row["count2"] = db.at[db[db["word"] == row["word2"]].index[0], "count"]

            # 積集合、jaccard係数の更新
            row["union_count"] = row["count1"] + row["count2"] - row["intersection_count"]
            row["jaccard_coefficient"] = float(row["intersection_count"]) / float(row["union_count"])
            return row
        self.__couple_words_count_frame = self.__couple_words_count_frame.apply(update_one_jaccard_coefficient,
                                                                                axis="columns")

    def delete_one_word(self, word):
        # TODO : imp
        pass

    def delete_couple_words(self, word1, word2):
        # TODO : imp
        pass

    def get_word_array(self):
        return self.__one_word_count_frame["word"].unique()

    def get_couple_nodes_frame(self):
        # [word1, word2, jaccard_coefficient]を
        # [node1, node2, value]のDataFrameで返す
        return self.__couple_words_count_frame.rename(
            columns={
                "word1": "node1",
                "word2": "node2",
                "jaccard_coefficient": "value"
            }
        )

    def debug_print(self):
        # dbをprintする
        print(self.__one_word_count_frame)
        print(self.__couple_words_count_frame)
