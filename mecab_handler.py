import MeCab
from enum import Enum
import pandas as pd
import itertools


class DataIndex(Enum):
    TITLE = 0
    FEATURE = 1


class MecabResultType(Enum):
    WORD_ONLY = 0
    ALL = 1


class MecabHandlerOption:
    def __init__(self):
        self.mecab_option = None


class WordDatabase:
    def __init__(self):
        self.one_word_count_frame = pd.DataFrame(columns=["word", "count"])
        self.couple_words_count_frame = pd.DataFrame(columns=["word1", "word2", "count"])
        pass

    def countup_word_list(self, word_list):
        # 複数単語を登録する
        for word in word_list:
            self.countup_one_word(word)

    def countup_one_word(self, word):
        db = self.one_word_count_frame
        extract_frame = db[db["word"] == word]

        row_num = len(extract_frame)
        if row_num == 0:
            # 行数が0の場合は新規追加
            s = pd.Series([word, 1], index=db.columns)
            self.one_word_count_frame = db.append(s, ignore_index=True)
        elif row_num == 1:
            # すでに追加されている場合はcountを+1する
            db.loc[db["word"] == word, "count"] = db.loc[db["word"] == word, "count"] + 1
        else:
            # 重複した単語がある場合は例外対応（TODO）
            print("{} is duplicated!".format(word))

    def countup_couple_words(self, word1, word2):
        db = self.couple_words_count_frame
        extract_frame = db[(db["word1"] == word1) & (db["word2"] == word2)]

        row_num = len(extract_frame)
        if row_num == 0:
            # 行数が0の場合は新規追加
            s = pd.Series([word1, word2, 1], index=db.columns)
            self.couple_words_count_frame = db.append(s, ignore_index=True)
        elif row_num == 1:
            # すでに追加されている場合はcountを+1する
            # TODO : もうちょっと良い感じに書けないだろうか・・
            db.loc[(db["word1"] == word1) & (db["word2"] == word2), "count"] \
                = db.loc[(db["word1"] == word1) & (db["word2"] == word2), "count"] + 1
        else:
            # 重複した単語がある場合は例外対応（TODO）
            print("{}/{} is duplicated!".format(word1, word2))

    def delete_one_word(self, word):
        # TODO : imp
        pass

    def delete_couple_words(self, word1, word2):
        # TODO : imp
        pass

    def debug_print(self):
        # dbをprintする
        print(self.one_word_count_frame)
        print(self.couple_words_count_frame)


class MecabHandler:
    def __init__(self, word_database=WordDatabase(), mecab_handler_option=MecabHandlerOption()):
        option = mecab_handler_option.mecab_option
        self.__tagger = MeCab.Tagger(option) if type(option) == "str" else MeCab.Tagger("")
        self.__word_database = word_database
        pass

    def parse(self, sentence, include_feature_list=None, result_type=MecabResultType.ALL):
        # 形態素解析の実施
        result = self.__tagger.parse(sentence)
        result = self.__convert_mecab_result(result,
                                             include_feature_list=include_feature_list,
                                             result_type=result_type)
        return result

    def parse_and_register(self, sentence):
        # 形態素解析の実施
        result = self.parse(sentence, include_feature_list=["名詞"], result_type=MecabResultType.WORD_ONLY)

        # DBに登録
        self.__register_word_db(result)

    def debug_print(self):
        # DBの中身をprint
        self.__word_database.debug_print()

    def __register_word_db(self, word_list):
        # 単語の出現数を登録
        self.__word_database.countup_word_list(word_list)

        # 共起単語（2単語のペア）の出現数を登録
        word_list = list(set(word_list))  # 重複除外のため、一度setに変換している
        combination_word_pairs = list(itertools.combinations(word_list, 2))
        for combination_word_pair in combination_word_pairs:
            self.__word_database.countup_couple_words(
                combination_word_pair[0],
                combination_word_pair[1]
            )

    # mecabの解析結果を配列に格納し直す。
    # mecabの解析結果は以下のようなイメージ
    # [本日	名詞,副詞可能,*,*,*,*,本日,ホンジツ,ホンジツ]
    # タブと[,]を処理すれば良い
    # 以下のような結果となる
    # [
    #    [本日, 名詞, ...],
    #    [...],...
    # ]
    def __convert_mecab_result(self, mecab_result, include_feature_list=None, result_type=MecabResultType.WORD_ONLY):
        mecab_format_results = []
        mecab_morpheme_list = mecab_result.split('\n')
        for line in mecab_morpheme_list:
            # mecabの出力結果では、EOSと空行が含まれるため、前述した行の場合は何も処理をしないようにする
            if line == '' or line == 'EOS':
                continue

            # mecabの解析結果を配列に格納し直す
            tmp_array = line.split('\t')
            tmp_array_2 = tmp_array[1].split(',')
            format_result = []
            format_result.append(tmp_array[0])
            format_result.extend(tmp_array_2)

            # 特定の品詞のみを追加する場合は、該当しない品詞は追加しない
            if include_feature_list is not None \
                    and not (format_result[DataIndex.FEATURE.value] in include_feature_list):
                continue

            # result typeに応じて、追加するデータを決める
            if result_type == MecabResultType.WORD_ONLY:
                format_result = format_result[DataIndex.TITLE.value]
            mecab_format_results.append(format_result)
        return mecab_format_results


if __name__ == "__main__":
    mh = MecabHandler()
    mh.parse_and_register("テストです、名詞を含めて下さい。明日は雨が降るでしょう。もう一度言います。明日は雨が降るでしょう。")
    mh.parse_and_register("テストです、名詞を含めて下さい。明日は雨が降るでしょう。もう一度言います。明日は雨が降るでしょう。")
    mh.debug_print()
