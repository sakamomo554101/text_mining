import argparse
import mecab_handler
import network_creator


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_txt_file",
                        help="input file. file type is text"
                        )
    parser.add_argument("--input_txt",
                        help="input text data."
                        )
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
    else:
        print("Error pattern. Please set 'input_txt_file' or 'input_txt' parameter.")
        exit(1)

    # 形態素解析を実施し、共起単語の重みを設定
    mecab_handler_option = mecab_handler.MecabHandlerOption()
    handler = mecab_handler.MecabHandler(mecab_handler_option=mecab_handler_option)
    handler.parse_and_register(txt)

    # 共起ネットワークを作成
    wd = handler.get_word_database()
    plot_option = network_creator.NetworkPlotOption()
    nc = network_creator.NetworkCreator(option=plot_option)
    nc.plot_graph(wd)


if __name__ == "__main__":
    main()
