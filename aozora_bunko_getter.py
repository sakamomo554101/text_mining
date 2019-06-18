# coding: UTF-8
import re
import os
import urllib.request as urllib
import zipfile
from enum import Enum
import glob


class AozoraBunkoFileUrl(Enum):
    NATSUME_KOKORO = ("kokoro", "https://www.aozora.gr.jp/cards/000148/files/773_ruby_5968.zip")


class AozoraBunkoGetter:
    def __init__(self, output_base_dir):
        self.__output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)

    def read_file(self, url, dir_name):
        # 文庫の圧縮ファイルを取得し、解凍
        extract_path = self.__download_file(url)
        output_dir = self.__extract_archive_file(extract_path, self.__output_base_dir, dir_name)

        # テキストファイルを読み込み、
        glob_path = os.path.join(output_dir, "*.txt")
        txt_path = glob.glob(glob_path)[0]
        return self.__convert_file(txt_path)

    def __download_file(self, url, overwrite=False):
        # zipファイル名の取得
        zip_file_name = re.split(r'/', url)[-1]
        extract_path = os.path.join(self.__output_base_dir, zip_file_name)

        # 指定したパスから文庫テキストファイルを作成する
        if os.path.isfile(extract_path) and not overwrite:
            print('File {} existed, skip.'.format(extract_path))
            return extract_path
        print('Downloading from url {} to {}'.format(url, extract_path))
        try:
            urllib.request.urlretrieve(url, extract_path)
        except:
            urllib.urlretrieve(url, extract_path)

        return extract_path

    def __extract_archive_file(self, zip_file_path, output_base_dir, dir_name, remove_archive=True):
        # 圧縮ファイル毎にフォルダを作成
        output_dir = os.path.join(output_base_dir, dir_name)
        os.makedirs(output_dir, exist_ok=True)

        # 解凍処理の実施
        zip_obj = zipfile.ZipFile(zip_file_path, 'r')
        zip_obj.extractall(output_dir)
        zip_obj.close()

        # 必要なら圧縮ファイルの削除
        if remove_archive:
            os.remove(zip_file_path)
        return output_dir

    def __convert_file(self, download_txt_path):
        # ダウンロードしたテキストファイルから文書データのみ（ルビなどを削除）を抽出する
        with open(download_txt_path, 'rb') as f:
            binarydata = f.read()
            text = binarydata.decode('shift_jis')

            # ルビ、注釈などの除去
            text = re.split(r'\-{5,}', text)[2]
            text = re.split(r'底本：', text)[0]
            text = re.sub(r'《.+?》', '', text)
            text = re.sub(r'［＃.+?］', '', text)
            text = text.strip()
            return text


if __name__ == "__main__":
    getter = AozoraBunkoGetter(output_base_dir="aozora")
    dir_name, url = AozoraBunkoFileUrl.NATSUME_KOKORO.value
    txt = getter.read_file(url=url, dir_name=dir_name)
    print(txt)
