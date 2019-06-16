import networkx as nx
from database import WordDatabase
import matplotlib.pyplot as plt
import os


class NetworkPlotOption:
    def __init__(self):
        self.fig_size = (15, 15)
        self.image_path = None
        self.file_name_without_ext = "word_network"
        self.ja_font_file = "AppleGothic"


class NetworkCreator:
    def __init__(self, option=NetworkPlotOption()):
        self.__option = option

    def plot_graph(self, word_database, edge_threshold=0.0):
        # 単語の一覧から、networkXを初期化
        word_list = word_database.get_word_array().tolist()
        g = nx.Graph()
        g.add_nodes_from(word_list)

        # edgeの重みを設定
        nodes_frame = word_database.get_couple_nodes_frame()
        for i in range(len(nodes_frame)):
            data = nodes_frame.iloc[i]
            if data["value"] > edge_threshold:
                g.add_edge(data["node1"], data["node2"], weight=data["value"])

        # 孤立したnodeを削除
        isolated_nodes = [n for n in g.nodes if g.degree(n) == 0]
        for n in isolated_nodes:
            g.remove_node(n)

        # プロットするグラフサイズの設定
        plt.figure(figsize=self.__option.fig_size)

        # ネットワーク情報を設定
        pos = nx.spring_layout(g, k=0.3)
        pr = nx.pagerank(g)

        # nodeの描画情報を設定
        nx.draw_networkx_nodes(g, pos, node_color=list(pr.values()),
                               cmap=plt.cm.Reds,
                               alpha=0.7,
                               node_size=[60000 * v for v in pr.values()])

        # edgeの描画情報を設定
        edge_width = [d["weight"] * 100 for (u, v, d) in g.edges(data=True)]
        nx.draw_networkx_edges(g, pos, alpha=0.4, edge_color="darkgrey", width=edge_width)

        # 日本語ラベルを設定
        nx.draw_networkx_labels(g, pos, fontsize=14, font_family=self.__option.ja_font_file, font_weight="bold")

        # プロットするグラフサイズの設定
        plt.axis('off')

        # グラフの保存
        self.__save_plt_image(
            dir_path=self.__option.image_path,
            file_name_without_ext=self.__option.file_name_without_ext
        )

    def __save_plt_image(self, dir_path, file_name_without_ext):
        if dir_path is not None and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

        # 保存する画像のフルパスを作成
        file_name = file_name_without_ext + ".png"
        full_path = file_name if dir_path is None else os.path.join(dir_path, file_name)

        # プロット画像の保存
        plt.savefig(full_path, bbox_inches="tight")


if __name__ == "__main__":
    word_database = WordDatabase()
    word_database.register_word_list(["テスト", "一応", "ホゲホゲ"])
    nc = NetworkCreator()
    nc.plot_graph(word_database)
