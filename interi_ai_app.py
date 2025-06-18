import asyncio
import io

import pandas as pd
import streamlit as st
import streamlit_antd_components as sac
from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, LLMConfig)
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from sitemapparser import SiteMapParser
from sitemapparser.exporters import JSONExporter


def init():
    st.set_page_config(page_title="Interior AI Demo ",
                       page_icon="🪑",
                       layout="wide",
                       initial_sidebar_state="collapsed")
    # セッションステート（家具選定）
    if 'furniture_condition_list' not in st.session_state:
        # カラム名とデータ型の辞書を定義
        column_types = {
            'テイスト': str,
            '納期': str,
            '価格帯': str,
            'カテゴリ': str,
            '幅': str,
            '奥行': str,
            '高さ': str,
            '座面高': str
        }
        st.session_state['furniture_condition_list'] = pd.DataFrame({
            col: pd.Series(dtype=dtype) for col, dtype in column_types.items()
        })
    # セッションステート（スクレイピング）
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


def validate_furniture_conditions(conditions):
    # 必要な条件がすべて設定されているかを確認
    required_str_conditions = ['テイスト', '納期']
    required_list_conditions = ['テイスト', '納期', '価格帯', 'カテゴリ', '幅', '奥行', '高さ', '座面高']
    for condition in required_str_conditions:
        if condition not in conditions or conditions[condition] == '':
            return False
    for condition in required_list_conditions:
        if condition not in conditions or (isinstance(conditions[condition], list) and
                                           len(conditions[condition]) == 0):
            return False
    return True


def add_furniture_condition_list(conditions):
    if validate_furniture_conditions(conditions) == False:
        st.error("選定条件が正しく設定されていません。")
        return

    new_condition = {
        'テイスト': conditions['テイスト'],
        '納期': conditions['納期'],
        '価格帯': conditions['価格帯'],
        'カテゴリ': conditions['カテゴリ'],
        '幅': f"{conditions['幅'][0]} - {conditions['幅'][1]} mm",
        '奥行': f"{conditions['奥行'][0]} - {conditions['奥行'][1]} mm",
        '高さ': f"{conditions['高さ'][0]} - {conditions['高さ'][1]} mm",
        '座面高': f"{conditions['座面高'][0]} - {conditions['座面高'][1]} mm"
    }
    # 新しい行をDataFrameとして作成
    new_row_df = pd.DataFrame([new_condition])

    # 既存のDataFrameに新しい行を追加
    st.session_state['furniture_condition_list'] = pd.concat(
        [st.session_state['furniture_condition_list'], new_row_df], ignore_index=True)


def search_conditions():
    with st.expander(label='選定条件', expanded=True):
        col1, col2 = st.columns(spec=2, gap='large', border=False)
        with col1:
            sac.divider(label='条件設定', icon='gear-fill', align='start', color='red')
            # テイスト
            with st.container(border=True):
                taste = sac.chip(items=[
                    sac.ChipItem(label='ナチュラル', icon='tree-fill'),
                    sac.ChipItem(label='インダストリアル', icon='building-fill'),
                ],
                                 label='テイスト',
                                 key='furniture_taste_chip',
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
                                    key='furniture_delivery_chip',
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
                                 key='furniture_price_chip',
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
                                        key='furniture_category_cascader',
                                        placeholder='カテゴリを選択してください（まだ全カテゴリ入れてません）',
                                        multiple=True,
                                        search=True,
                                        clear=True)
            # サイズ
            with st.container(border=True):
                st.caption('サイズ')
                col1_1, col1_2 = st.columns(spec=2, gap='large', border=False)
                with col1_1:
                    # 幅
                    witdh = st.slider(label='幅',
                                      key='furniture_width_slider',
                                      min_value=0,
                                      max_value=8000,
                                      value=(0, 8000),
                                      step=100,
                                      format='%d mm',
                                      help='幅の範囲を選択してください。')
                    # 奥行
                    depth = st.slider(label='奥行',
                                      key='furniture_depth_slider',
                                      min_value=0,
                                      max_value=4000,
                                      value=(0, 4000),
                                      step=100,
                                      format='%d mm',
                                      help='奥行の範囲を選択してください。')
                with col1_2:
                    # 高さ
                    height = st.slider(label='高さ',
                                       key='furniture_height_slider',
                                       min_value=0,
                                       max_value=3000,
                                       value=(0, 3000),
                                       step=100,
                                       format='%d mm',
                                       help='高さの範囲を選択してください。')
                    # 座面高
                    sheet_height = st.slider(label='座面高',
                                             key='furniture_sheet_height_slider',
                                             min_value=0,
                                             max_value=3000,
                                             value=(0, 3000),
                                             step=100,
                                             format='%d mm',
                                             help='座面高の範囲を選択してください。')
            # 条件をまとめる
            conditions = {
                'テイスト': taste,
                '納期': delivery,
                '価格帯': price,
                'カテゴリ': category,
                '幅': witdh,
                '奥行': depth,
                '高さ': height,
                '座面高': sheet_height
            }

            if st.button(label='選定条件を保存',
                         icon='💾',
                         disabled=not validate_furniture_conditions(conditions),
                         use_container_width=True):
                # 選定条件を保存
                add_furniture_condition_list(conditions)
        with col2:
            sac.divider(label='条件一覧', icon='card-checklist', align='start', color='red')
            # 選定条件一覧
            with st.container(border=True):
                st.dataframe(st.session_state['furniture_condition_list'],
                             hide_index=True,
                             on_select="rerun",
                             selection_mode="multi-row")


def chat_input():
    prompt = st.chat_input(placeholder="その他にもご要望があれば入力してください。", accept_file=True)
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
    scraping_flag = False

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
                                value='https://www.asplund-contract.com/product-sitemap.xml',
                                placeholder='https://example.com/sitemap.xml',
                                help='XMLサイトマップのURLを入力してください。')
        elif data_source_type == 1:  # URL
            url = st.text_input(label='URLを入力してください',
                                value='https://www.asplund-contract.com/product/br/workplus/',
                                placeholder='https://example.com',
                                help='スクレイピングしたいページのURLを入力してください。')
        else:
            url = ''

        # URL解析ボタン
        url_analyze_flag = st.button(label='URL解析',
                                     icon='🔍',
                                     use_container_width=True,
                                     disabled=True if url == '' else False)

    # URL一覧のDataFrame
    df_urls = pd.DataFrame()

    # URL解析
    if url_analyze_flag:
        if data_source_type == 0:  # XMLサイトマップ
            sm = SiteMapParser(url)  # reads /sitemap.xml
            json_exporter = JSONExporter(sm)
            if sm.has_urls():
                df_urls = pd.read_json(io.StringIO(json_exporter.export_urls()))
                df_urls.drop(columns=['lastmod', 'changefreq', 'priority'], inplace=True)
                df_urls.rename(columns={'loc': 'URL'}, inplace=True)
        elif data_source_type == 1:  # URL
            # asyncio.run(scrape_item_list(url))
            st.write("未実装")

    else:
        df_urls = st.session_state['scraping_all_url_list']

    if len(df_urls) > 0:
        with st.expander(label='URL一覧', expanded=True):
            st.session_state['scraping_all_url_list'] = df_urls
            selection = st.dataframe(df_urls,
                                     column_config={
                                         "URL": st.column_config.LinkColumn("URL")
                                     },
                                     use_container_width=True,
                                     hide_index=True,
                                     on_select="rerun",
                                     selection_mode="multi-row").selection
            # 選択されたURLをセッションステートに保存
            if selection.rows:
                st.session_state['scraping_selected_url_list'] = df_urls.iloc[selection.rows, :]
            else:
                st.session_state['scraping_selected_url_list'] = pd.DataFrame()

            # スクレイピングボタン
            if len(st.session_state['scraping_selected_url_list']) > 0:
                scraping_flag = st.button(label='スクレイピング', icon='🕷️', use_container_width=True)

    # スクレイピング
    if scraping_flag:
        with st.expander(label='スクレイピング', expanded=True):
            scraped_data = asyncio.run(
                scrape_data(st.session_state['scraping_selected_url_list']['URL'].tolist()))
            st.text_area(label='スクレイピング結果', value=scraped_data, height=300, disabled=True)
            st.button(label='データを保存', icon='💾', use_container_width=True)


async def scrape_data(urls):

    class ProductInfo(BaseModel):
        brand_name: str = Field(..., description="ブランド名を表す文字列")
        item_name: str = Field(..., description="アイテム名を表す文字列")
        size: str = Field(..., description="サイズを表す文字列. 例：W500 D500 H550 ")
        weight: str = Field(..., description="重量を表す文字列. 例：15kg")
        material: str = Field(..., description="素材を表す文字列. 例：Fabric, Steel")
        price: str = Field(..., description="価格を表す文字列. 例：￥120,000（税込）")
        description: str = Field(...,
                                 description="商品説明を表す文字列. 例：このソファは、快適な座り心地とスタイリッシュなデザインを兼ね備えています。")
        image_urls: list[str] = Field(..., description="商品画像のURLリスト")  # 画像のURLリスト

    browser_config = BrowserConfig(
        user_agent_mode="random",  # ボット検出に対抗
        verbose=True,
        # headless=False
    )
    # Define the LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider="gemini/gemini-2.5-flash",
                             api_token=st.secrets['GEMINI_API_TOKEN']),
        schema=ProductInfo.model_json_schema(),
        extraction_type="schema",
        # extraction_type="block",
        verbose=True,
        instruction='''
与えられたコンテンツを、以下のJSON形式に変換して出力してください。\n\n
プログラムコードではなく、JSON形式のデータを出力します。
JSON以外の文字やコメントは絶対に絶対に絶対に出力しないでください。

# 以下の条件を必ず守ってください:
- 結果は厳密なJSONオブジェクトを返すこと
- JSON以外の文字やコメントは絶対に絶対に絶対に出力しない
# 出力例
{
  "brand_name": "ここにブランド名",
  "item_name": "ここに商品名を出力",
  "size": "ここにサイズをmm単位に変換して出力",
  "weight": "ここに重量をkg単位に変換して出力",
  "material": "ここに素材を出力",
  "price": "ここに価格を日本円で出力（税込/税抜がわかるように記載）",
  "description": "ここに商品説明を出力",
  "image_urls": [
    "https://example.com/images/item1.jpg",
    "https://example.com/images/item2.jpg",
    "https://example.com/images/item3.jpg"
  ]
}
''',
        chunk_token_threshold=65536,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",  # or "html", "fit_markdown"
        extra_args={
            "temperature": 0.0,
            "max_tokens": 65536
        })
    run_config = CrawlerRunConfig(
        excluded_tags=['header', 'footer', 'nav'],  # 除外するタグ
        extraction_strategy=llm_strategy,
        # word_count_threshold=10,  # Minimum words per content block. サイトに短い段落や項目が多数ある場合、ブロックが考慮される前の最小単語数を下げる
        exclude_external_links=True,  # Remove external links
        exclude_social_media_links=True,  # Remove social media links
        exclude_external_images=True,  # Remove external images
        remove_overlay_elements=True,  # Remove popups/modals
        process_iframes=True,  # Process iframe content
        verbose=True)

    scraped_data = ''
    for url in urls:
        async with AsyncWebCrawler(config=browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if result.success:
                # st.write("markdown")
                # st.write(result.markdown)
                # LLMExtractionStrategyを使用している場合、result.markdownに抽出されたデータが含まれる
                st.write(f"LLM: \n\n{result.extracted_content}")
                st.write(f"markdown: \n\n{result.markdown}")
                scraped_data += f"{result.markdown}\n\n"
                # st.write("media")
                # for image in result.media["images"]:
                #     st.image(image['src'], caption=image['alt'])
                # st.write("links")
                # for link in result.links["internal"]:
                #     st.markdown(f"[{link['text']}]({link['href']})")
            else:
                st.error(
                    f"Failed to scrape {url}: status_code:{result.status_code} message:{result.error_message}"
                )
                continue

    return scraped_data


async def scrape_item_list(url):
    browser_config = BrowserConfig(
        user_agent_mode="random",  # ボット検出に対抗
        verbose=True,
        # headless=False
    )
    run_config = CrawlerRunConfig(
        excluded_tags=['header', 'footer', 'nav'],  # 除外するタグ
        # word_count_threshold=10,  # Minimum words per content block. サイトに短い段落や項目が多数ある場合、ブロックが考慮される前の最小単語数を下げる
        exclude_external_links=True,  # Remove external links
        exclude_social_media_links=True,  # Remove social media links
        exclude_external_images=True,  # Remove external images
        remove_overlay_elements=True,  # Remove popups/modals
        process_iframes=True  # Process iframe content
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        if result.success:
            st.write("markdown")
            st.write(result.markdown)
            # st.write("media")
            # for image in result.media["images"]:
            #     st.image(image['src'], caption=image['alt'])
            # st.write("links")
            # for link in result.links["internal"]:
            #     st.markdown(f"[{link['text']}]({link['href']})")
        else:
            st.error(
                f"Failed to scrape {url}: status_code:{result.status_code} message:{result.error_message}"
            )


async def deep_crawl_test(url):
    config = CrawlerRunConfig(deep_crawl_strategy=BFSDeepCrawlStrategy(max_depth=0,
                                                                       include_external=False),
                              scraping_strategy=LXMLWebScrapingStrategy(),
                              verbose=True)

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(url, config=config)

        st.write(f"Crawled {len(results)} pages in total")

        # Access individual results
        for result in results[:3]:  # Show first 3 results
            st.write(f"URL: {result.url}")
            st.write(f"Depth: {result.metadata.get('depth', 0)}")
            st.write(result.markdown)  # Show first 500 characters of markdown


if __name__ == "__main__":
    # 初期化
    init()
    # サイドバーの表示
    menu = sidebar()
    # メインコンテンツの表示
    if menu == '家具選定':
        # 選定条件の表示
        search_conditions()
        #
        if st.button(label='保存した条件で検索',
                     icon='🔍',
                     disabled=len(st.session_state['furniture_condition_list']) == 0,
                     use_container_width=True):
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

        # チャット入力
        chat_input()
    elif menu == 'スクレイピング':
        scrapintg()
    elif menu == 'PDFデータ抽出':
        st.write("未実装")
    else:
        st.write("")

    # with st.expander(label='session', expanded=False):
    #     st.write(st.session_state)
