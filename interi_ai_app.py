import pandas as pd
import streamlit as st
import streamlit_antd_components as sac


def init():
    st.set_page_config(page_title="Interior AI Demo ",
                       page_icon="🪑",
                       layout="wide",
                       initial_sidebar_state="collapsed")
    # セッション
    if 'scraping_data_source_type' not in st.session_state:
        st.session_state['scraping_data_source_type'] = 0
    if 'scraping_all_url_list' not in st.session_state:
        st.session_state['scraping_all_url_list'] = pd.DataFrame()
    if 'scraping_selected_url_list' not in st.session_state:
        st.session_state['scraping_selected_url_list'] = pd.DataFrame()


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
    with st.expander(label='選定条件', expanded=True):
        # テイスト
        with st.container(border=True):
            taste = sac.chip(items=[
                sac.ChipItem(label='ナチュラル', icon='tree-fill'),
                sac.ChipItem(label='インダストリアル', icon='building-fill'),
            ],
                             label='テイスト',
                             align='start',
                             radius='xl',
                             variant='light',
                             multiple=False)

        # 納期
        with st.container(border=True):
            delivery = sac.chip(items=[
                sac.ChipItem(label='在庫品', icon='truck-fill'),
                sac.ChipItem(label='3週間', icon='calendar-check-fill'),
                sac.ChipItem(label='1ヶ月', icon='calendar-check-fill'),
                sac.ChipItem(label='1.5〜2ヶ月', icon='calendar-check-fill'),
            ],
                                label='納期',
                                align='start',
                                radius='xl',
                                variant='outline',
                                multiple=False)

        # 価格帯
        with st.container(border=True):
            price = sac.chip(items=[
                sac.ChipItem(label='Low', icon='cash-coin'),
                sac.ChipItem(label='Middle', icon='cash-coin'),
                sac.ChipItem(label='High', icon='cash-coin')
            ],
                             label='価格帯',
                             align='start',
                             radius='xl',
                             variant='outline',
                             multiple=True)
        # カテゴリ
        with st.container(border=True):
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
                                    label='カテゴリ',
                                    placeholder='カテゴリを選択してください（まだ全カテゴリ入れてません）',
                                    multiple=True,
                                    search=True,
                                    clear=True)
        # サイズ
        with st.container(border=True):
            st.caption('サイズ')
            col1, col2, col3, col4 = st.columns(spec=4, gap='large')
            with col1:
                # 幅
                witdh = st.slider(label='幅',
                                  min_value=0,
                                  max_value=8000,
                                  value=(0, 8000),
                                  step=100,
                                  format='%d mm',
                                  help='幅の範囲を選択してください。')
            with col2:
                # 奥行
                depth = st.slider(label='奥行',
                                  min_value=0,
                                  max_value=4000,
                                  value=(0, 4000),
                                  step=100,
                                  format='%d mm',
                                  help='奥行の範囲を選択してください。')
            with col3:
                # 高さ
                height = st.slider(label='高さ',
                                   min_value=0,
                                   max_value=3000,
                                   value=(0, 3000),
                                   step=100,
                                   format='%d mm',
                                   help='高さの範囲を選択してください。')
            with col4:
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


def scrapintg():
    url_analyze_flag = False
    scraping_test_flag = False
    scraping_all_flag = False

    # データソース
    with st.expander(label='データソース', expanded=True):
        data_source_type = sac.segmented(
            items=[
                sac.SegmentedItem(label='XMLサイトマップ'),
                sac.SegmentedItem(label='URL'),
            ],
            return_index=True,
            label='',
            size='sm',
            radius='sm',
            align='center',
            key='scraping_data_source_type',
        )

        url = ''
        if data_source_type == 0:  # XMLサイトマップ
            url = st.text_input(label='XMLサイトマップのURLを入力してください',
                                placeholder='https://example.com/sitemap.xml',
                                help='XMLサイトマップのURLを入力してください。')
        elif data_source_type == 1:  # URL
            url = st.text_input(label='URLを入力してください',
                                placeholder='https://example.com',
                                help='スクレイピングしたいページのURLを入力してください。')
        else:
            url = ''

        # URL解析ボタン
        url_analyze_flag = st.button(label='URL解析',
                                     icon='🔍',
                                     use_container_width=True,
                                     disabled=True if url == '' else False)

    # URL一覧
    if url_analyze_flag or len(st.session_state['scraping_all_url_list']) > 0:
        # ここにスクレイピングの処理を追加
        with st.expander(label='URL一覧', expanded=True):
            df = pd.DataFrame([
                {
                    "URL": "https://example.com/product1"
                },
                {
                    "URL": "https://example.com/product2"
                },
                {
                    "URL": "https://example.com/product3"
                },
            ])
            st.session_state['scraping_all_url_list'] = df
            selection = st.dataframe(df,
                                     column_config={
                                         "URL": st.column_config.LinkColumn("URL")
                                     },
                                     use_container_width=True,
                                     hide_index=True,
                                     on_select="rerun",
                                     selection_mode="multi-row").selection
            # 選択されたURLをセッションステートに保存
            if selection.rows:
                st.session_state['scraping_selected_url_list'] = df.iloc[selection.rows, :]
            else:
                st.session_state['scraping_selected_url_list'] = pd.DataFrame()

            # スクレイピングテストボタン
            if len(st.session_state['scraping_selected_url_list']) > 0:
                scraping_test_flag = st.button(label='スクレイピング【テスト実行】',
                                               icon='🧪',
                                               use_container_width=True)
            # スクレイピング実行ボタン
            if len(st.session_state['scraping_all_url_list']) > 0:
                scraping_all_flag = st.button(label='スクレイピング【全実行】',
                                              icon='🕷️',
                                              use_container_width=True)

    # スクレイピングテスト
    if scraping_test_flag:
        with st.expander(label='スクレイピングテスト', expanded=True):
            # ここにスクレイピングのテスト結果を表示する処理を追加
            st.write("スクレイピングテストを実行しました。")
    # スクレイピング結果
    if scraping_all_flag:
        with st.expander(label='スクレイピング結果', expanded=True):
            # ここにスクレイピングの結果を表示する処理を追加
            st.write("スクレイピング結果を表示します。")
            st.button(label='データを保存', icon='💾', use_container_width=True)


if __name__ == "__main__":
    # 初期化
    init()
    # サイドバーの表示
    menu = sidebar()
    # メインコンテンツの表示
    if menu == '家具選定':
        conditions = search_conditions()
        # st.write(conditions)
        chat_input()
    elif menu == 'スクレイピング':
        scrapintg()
    elif menu == 'PDFデータ抽出':
        st.write("未実装")
    else:
        st.write("")

    # with st.expander(label='session', expanded=False):
    #     st.write(st.session_state)
