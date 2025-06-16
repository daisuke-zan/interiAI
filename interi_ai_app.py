import streamlit as st
import streamlit_antd_components as sac


def init():
    st.set_page_config(page_title="Interior AI Demo ",
                       page_icon="🪑",
                       layout="wide",
                       initial_sidebar_state="collapsed")


def sidebar():
    with st.sidebar:
        selected_menu = sac.menu([
            sac.MenuItem('家具選定', icon='house-door-fill'),
            sac.MenuItem('商品データ作成',
                         icon='database-fill',
                         children=[
                             sac.MenuItem('スクレイピング', icon='globe'),
                             sac.MenuItem('PDFデータ抽出', icon='filetype-pdf')
                         ])
        ],
                                 open_all=True)
    return selected_menu


def search_conditions():
    with st.container():
        # テイスト
        with st.expander(label='テイスト', expanded=True):
            taste = sac.chip(items=[
                sac.ChipItem(label='ナチュラル', icon='tree-fill'),
                sac.ChipItem(label='インダストリアル', icon='building-fill'),
            ],
                             label='',
                             align='start',
                             radius='xl',
                             variant='light',
                             multiple=False)

        # 納期
        with st.expander(label='納期', expanded=True):
            delivery = sac.chip(items=[
                sac.ChipItem(label='在庫品', icon='truck-fill'),
                sac.ChipItem(label='3週間', icon='calendar-check-fill'),
                sac.ChipItem(label='1ヶ月', icon='calendar-check-fill'),
                sac.ChipItem(label='1.5〜2ヶ月', icon='calendar-check-fill'),
            ],
                                label='',
                                align='start',
                                radius='xl',
                                variant='outline',
                                multiple=False)

        # 価格帯
        with st.expander(label='価格帯', expanded=True):
            price = sac.chip(items=[
                sac.ChipItem(label='Low', icon='cash-coin'),
                sac.ChipItem(label='Middle', icon='cash-coin'),
                sac.ChipItem(label='High', icon='cash-coin')
            ],
                             label='',
                             align='start',
                             radius='xl',
                             variant='outline',
                             multiple=True)
        # カテゴリ
        with st.expander(label='カテゴリ', expanded=True):
            category = sac.cascader(items=[
                sac.CasItem('ソファ',
                            children=[
                                sac.CasItem('1人掛けソファ'),
                                sac.CasItem('2人掛けソファ'),
                                sac.CasItem('3人掛けソファ'),
                            ]),
                sac.CasItem('チェア・椅子',
                            children=[
                                sac.CasItem('オフィスチェア・ワークチェア'),
                                sac.CasItem('ミーティングチェア'),
                                sac.CasItem('ダイニングチェア'),
                            ]),
            ],
                                    label='',
                                    placeholder='カテゴリを選択してください（まだ全カテゴリ入れてません）',
                                    multiple=True,
                                    search=True,
                                    clear=True)
        # サイズ
        with st.expander(label='サイズ', expanded=True):
            # 幅
            witdh = st.slider(label='幅',
                              min_value=0,
                              max_value=8000,
                              value=(0, 8000),
                              step=100,
                              format='%d mm',
                              help='幅の範囲を選択してください。')
            # 奥行
            depth = st.slider(label='奥行',
                              min_value=0,
                              max_value=4000,
                              value=(0, 4000),
                              step=100,
                              format='%d mm',
                              help='奥行の範囲を選択してください。')
            # 高さ
            height = st.slider(label='高さ',
                               min_value=0,
                               max_value=3000,
                               value=(0, 3000),
                               step=100,
                               format='%d mm',
                               help='高さの範囲を選択してください。')
            # 座面高
            sheet_height = st.slider(label='座面高',
                                     min_value=0,
                                     max_value=3000,
                                     value=(0, 3000),
                                     step=100,
                                     format='%d mm',
                                     help='座面高の範囲を選択してください。')

    # チップの選択結果を表示
    conditions = {
        'テイスト': taste if taste != '' else '未選択',
        '納期': delivery if delivery != '' else '未選択',
        '価格帯': price if price != '' else '未選択',
        'カテゴリ': category if category != '' else '未選択',
        '幅': witdh,
        '奥行': depth,
        '高さ': height,
        '座面高': sheet_height
    }
    return conditions


def chat_input():
    prompt = st.chat_input(placeholder="検索したい家具のイメージを入力してください。", accept_file=True)
    if prompt:
        # st.write(f"User has sent the following prompt: {prompt}")
        with st.chat_message(name="assistant"):
            st.markdown('''
こちらの商品はいかがでしょうか？  
商品名：[PENTE 1P SOFA](https://www.asplund-contract.com/product/12426/)  
ブランド：Work Plus
Size:W760 D760 H670 SH425  
Material:Fabric, Steel  
Price:￥120,000  
![PENTE 1P SOFA](https://www.asplund-contract.com/wp-content/uploads/2024/06/wp_pente1psofa-3-600x600.jpg)
  
  
商品名：[MELTONE 1P SOFA](https://www.asplund-contract.com/product/12396/)  
ブランド：Work Plus
Size:W870 D720 H750 SH410
Material:Fabric, Steel  
Price:￥110,000  
![PENTE 1P SOFA](https://www.asplund-contract.com/wp-content/uploads/2024/06/wp_meltone1psofa-1-600x600.jpg)
''')


if __name__ == "__main__":
    # 初期化
    init()
    # サイドバーの表示
    menu = sidebar()
    # メインコンテンツの表示
    if menu == '家具選定':
        col1, col2 = st.columns([3, 7])
        with col1:
            with st.container(border=True):
                conditions = search_conditions()
                # st.write(conditions)
        with col2:
            with st.container(border=True):
                chat_input()
    elif menu == 'スクレイピング':
        st.write("未実装")
    elif menu == 'PDFデータ抽出':
        st.write("未実装")
    else:
        st.write("")
