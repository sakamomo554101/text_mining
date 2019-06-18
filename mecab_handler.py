import MeCab
from enum import Enum
from database import WordDatabase
import re


class DataIndex(Enum):
    TITLE = 0
    FEATURE = 1


class MecabResultType(Enum):
    WORD_ONLY = 0
    ALL = 1


class MecabHandlerOption:
    def __init__(self):
        self.mecab_option = None
        self.split_pattern = "[!！。?？]"  # テキストを1文ずつに分割する場合の正規表現パターン


class MecabHandler:
    def __init__(self, word_database=WordDatabase(), mecab_handler_option=MecabHandlerOption()):
        self.__option = mecab_handler_option
        self.__tagger = MeCab.Tagger(self.__option.mecab_option) if type(self.__option.mecab_option) == "str" else MeCab.Tagger("")
        self.__word_database = word_database

    def __parse(self, sentence, include_feature_list=None, result_type=MecabResultType.ALL):
        # 形態素解析の実施
        result = self.__tagger.parse(sentence)
        result = self.__convert_mecab_result(result,
                                             include_feature_list=include_feature_list,
                                             result_type=result_type)
        return result

    def parse_and_register(self, txt):
        print("## start to parse txt... ##")

        # テキストを句読点で分割
        sentences = self.__split_sentence(txt)
        sentence_count = len(sentences)

        # 文章ごとに解析を実施
        for i, sentence in enumerate(sentences):
            print("## {}/{} sentence parse start.. ##".format(i+1, sentence_count))

            # 形態素解析の実施
            result = self.__parse(sentence, include_feature_list=["名詞"], result_type=MecabResultType.WORD_ONLY)

            # DBに登録
            self.__register_word_db(result)

        # 最後のDBをアップデートする
        self.__word_database.update_jaccard_coefficient()

    def get_word_database(self):
        return self.__word_database

    def debug_print(self):
        # DBの中身をprint
        self.__word_database.debug_print()

    def __register_word_db(self, word_list):
        self.__word_database.register_word_list(word_list)

    def __split_sentence(self, txt):
        pattern = self.__option.split_pattern
        return re.split(pattern, txt)

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
