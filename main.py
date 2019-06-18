import argparse
import mecab_handler
import network_creator
from aozora_bunko_getter import AozoraBunkoGetter, AozoraBunkoFileUrl
import time


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_txt_file",
                        help="input file. file type is text"
                        )
    parser.add_argument("--input_txt",
                        help="input text data."
                        )
    parser.add_argument("--use_aozora_bunko", action="store_true")
    return parser.parse_args()


def main():
    # 引数に指定された文字列を取得
    args = get_args()
    if args.input_txt_file is not None:
        path = args.input_txt_file
        with open(path) as f:
            txt = f.read()
    elif args.input_txt is not None:
        txt = args.input_txt
    elif args.use_aozora_bunko:
        # TODO : 青空文庫の内容毎に条件分岐する
        getter = AozoraBunkoGetter(output_base_dir="aozora")
        dir_name, url = AozoraBunkoFileUrl.NATSUME_KOKORO.value
        txt = getter.read_file(url=url, dir_name=dir_name)
    else:
        print("Error pattern. Please set 'input_txt_file' or 'input_txt' parameter.")
        exit(1)

    # 実行時間を計測（開始）
    start_time = time.time()

    # 形態素解析を実施し、共起単語の重みを設定
    mecab_handler_option = mecab_handler.MecabHandlerOption()
    handler = mecab_handler.MecabHandler(mecab_handler_option=mecab_handler_option)
    handler.parse_and_register(txt)

    # 共起ネットワークを作成
    wd = handler.get_word_database()
    plot_option = network_creator.NetworkPlotOption()
    nc = network_creator.NetworkCreator(option=plot_option)
    nc.plot_graph(wd)

    # 実行時間を計測（終了）
    execute_time = time.time() - start_time
    print("## execute time is {}".format(execute_time))


if __name__ == "__main__":
    main()
