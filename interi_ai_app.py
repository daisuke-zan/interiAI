import streamlit as st
import streamlit_antd_components as sac


def sidebar():
    # Custom CSS to modify sidebar width
    st.markdown("""
        <style>
        [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
            width: 500px;
        }
        [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
            width: 500px;
            margin-left: -500px;
        }
        </style>
        """,
                unsafe_allow_html=True)
    with st.sidebar:
        conditions = search_conditions()

    return conditions


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
                sac.ChipItem(label='Low', icon='cash-stack'),
                sac.ChipItem(label='Middle', icon='cash-stack'),
                sac.ChipItem(label='High', icon='cash-stack')
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
    conditions = sidebar()
    # st.write(conditions)
    chat_input()
