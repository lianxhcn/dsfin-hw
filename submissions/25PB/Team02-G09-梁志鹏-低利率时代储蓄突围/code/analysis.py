"""
核心分析脚本 - 低利率时代的储蓄突围
生成所有核心图表
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from datetime import datetime
import os
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'Heiti TC']
plt.rcParams['axes.unicode_minus'] = False

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, 'data_raw')
OUT_DIR = os.path.join(BASE_DIR, 'output', 'charts')
os.makedirs(OUT_DIR, exist_ok=True)

# ===================== 数据读取 =====================
df_deposit = pd.read_csv(os.path.join(RAW_DIR, 'deposit_rate.csv'))
df_lpr = pd.read_csv(os.path.join(RAW_DIR, 'lpr_rate.csv'))
df_bond = pd.read_csv(os.path.join(RAW_DIR, 'bond_yield.csv'))
df_cpi = pd.read_csv(os.path.join(RAW_DIR, 'cpi.csv'))
df_m2 = pd.read_csv(os.path.join(RAW_DIR, 'money_supply.csv'))
df_money = pd.read_csv(os.path.join(RAW_DIR, 'money_fund.csv'))
df_gold = pd.read_csv(os.path.join(RAW_DIR, 'gold_futures.csv'))

# 读取债券基金净值
bond_funds = {
    '003327': '鹏华丰禄债券',
    '006962': '中短债债券A',
    '000032': '易方达信用债A',
    '000191': '富国信用债A',
    '000171': '易方达裕祥回报',
}
df_bonds = {}
for code, name in bond_funds.items():
    df = pd.read_csv(os.path.join(RAW_DIR, f'bond_fund_{code}.csv'))
    df_bonds[code] = df

print("数据读取完成")

# ===================== 图1：存款利率下行趋势 =====================
fig, ax1 = plt.subplots(figsize=(14, 7))

# 存款利率
df_deposit['日期'] = pd.to_datetime(df_deposit['日期'])
ax1.plot(df_deposit['日期'], df_deposit['1年期定存利率'],
         marker='o', markersize=3, linewidth=2, color='#E74C3C', label='1年期定存利率')

# LPR数据
df_lpr['TRADE_DATE'] = pd.to_datetime(df_lpr['TRADE_DATE'])
df_lpr_recent = df_lpr[df_lpr['TRADE_DATE'] >= '2019-01-01']
ax1.plot(df_lpr_recent['TRADE_DATE'], df_lpr_recent['RATE_1'],
         linestyle='--', linewidth=1.5, color='#3498DB', alpha=0.7, label='1年期贷款利率(LPR参考)')

ax1.set_xlabel('年份', fontsize=12)
ax1.set_ylabel('利率 (%)', fontsize=12, color='#E74C3C')
ax1.tick_params(axis='y', labelcolor='#E74C3C')
ax1.set_title('中国存款利率历史性下行（1993-2025）', fontsize=16, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3)
ax1.set_ylim(0, 12)

# 添加关键时间节点注释
ax1.annotate('10.98%', xy=(pd.Timestamp('1993-07-11'), 10.98),
            xytext=(pd.Timestamp('1995-01-01'), 11.5),
            fontsize=9, color='#E74C3C',
            arrowprops=dict(arrowstyle='->', color='#E74C3C', alpha=0.7))
ax1.annotate('1.10%', xy=(pd.Timestamp('2024-10-18'), 1.10),
            xytext=(pd.Timestamp('2022-01-01'), 2.5),
            fontsize=9, color='#E74C3C',
            arrowprops=dict(arrowstyle='->', color='#E74C3C', alpha=0.7))
ax1.annotate('历史最低', xy=(pd.Timestamp('2024-10-18'), 1.10),
            xytext=(pd.Timestamp('2024-10-18'), 0.3),
            fontsize=10, color='#E74C3C', ha='center',
            arrowprops=dict(arrowstyle='->', color='#E74C3C', alpha=0.7))

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig1_deposit_rate_trend.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图1 已保存")

# ===================== 图2：国债收益率走势 =====================
fig, ax = plt.subplots(figsize=(14, 7))

df_bond['日期'] = pd.to_datetime(df_bond['日期'])
df_bond = df_bond.sort_values('日期')

ax.plot(df_bond['日期'], df_bond['中国国债收益率2年'], label='2年期', linewidth=1.5, color='#3498DB')
ax.plot(df_bond['日期'], df_bond['中国国债收益率5年'], label='5年期', linewidth=1.5, color='#2ECC71')
ax.plot(df_bond['日期'], df_bond['中国国债收益率10年'], label='10年期', linewidth=2, color='#E74C3C')
ax.plot(df_bond['日期'], df_bond['中国国债收益率30年'], label='30年期', linewidth=1.5, color='#9B59B6')

ax.set_xlabel('年份', fontsize=12)
ax.set_ylabel('收益率 (%)', fontsize=12)
ax.set_title('中国国债收益率走势（2015-2025）', fontsize=16, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)

# 添加当前水平标注
latest = df_bond.iloc[-1]
ax.axhline(y=latest['中国国债收益率10年'], color='#E74C3C', linestyle=':', alpha=0.5)
ax.text(df_bond['日期'].iloc[-1], latest['中国国债收益率10年'] + 0.05,
        f'10年期: {latest["中国国债收益率10年"]:.2f}%',
        fontsize=10, color='#E74C3C', ha='right')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig2_bond_yield_trend.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图2 已保存")

# ===================== 图3：实际利率（存款利率 - CPI）====================
fig, ax = plt.subplots(figsize=(14, 7))

# CPI同比
df_cpi_clean = df_cpi.copy()
df_cpi_clean['月份'] = df_cpi_clean['月份'].str.replace('年', '-').str.replace('月份', '')
df_cpi_clean['日期'] = pd.to_datetime(df_cpi_clean['月份'], format='%Y-%m', errors='coerce')
df_cpi_clean = df_cpi_clean.dropna(subset=['日期']).sort_values('日期')

# 合并存款利率和CPI
df_real = df_deposit.copy()
df_real = df_real.set_index('日期').reindex(df_cpi_clean['日期'], method='ffill').reset_index()
df_real = df_real.rename(columns={'index': '日期'})
df_real['CPI同比'] = df_cpi_clean['全国-同比增长'].values
df_real['实际利率'] = df_real['1年期定存利率'] - df_real['CPI同比']

ax.plot(df_real['日期'], df_real['1年期定存利率'], label='名义利率', linewidth=2, color='#E74C3C')
ax.plot(df_real['日期'], df_real['CPI同比'], label='CPI同比', linewidth=2, color='#3498DB')
ax.plot(df_real['日期'], df_real['实际利率'], label='实际利率', linewidth=2, color='#2ECC71')
ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)

ax.set_xlabel('年份', fontsize=12)
ax.set_ylabel('百分比 (%)', fontsize=12)
ax.set_title('名义利率 vs CPI vs 实际利率', fontsize=16, fontweight='bold')
ax.legend(loc='upper right', fontsize=11)
ax.grid(True, alpha=0.3)

# 标注实际利率为负的时期
df_neg = df_real[df_real['实际利率'] < 0]
if not df_neg.empty:
    ax.fill_between(df_neg['日期'], 0, df_neg['实际利率'], alpha=0.2, color='red', label='实际利率为负')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig3_real_interest_rate.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图3 已保存")

# ===================== 图4：收益-风险全景散点图 =====================
# 计算各渠道的收益和风险
channels = []

# 1. 1年期定存
current_deposit = df_deposit['1年期定存利率'].iloc[-1]
channels.append({'产品': '1年期定存', '年化收益率%': current_deposit, '波动率%': 0.0, '最大回撤%': 0.0, '类型': '存款'})

# 2. 3年期国债（用当前10年期近似）
latest_bond = df_bond.iloc[-1]
channels.append({'产品': '10年期国债', '年化收益率%': latest_bond['中国国债收益率10年'], '波动率%': 2.0, '最大回撤%': 3.0, '类型': '国债'})
channels.append({'产品': '2年期国债', '年化收益率%': latest_bond['中国国债收益率2年'], '波动率%': 0.5, '最大回撤%': 1.0, '类型': '国债'})

# 3. 货币基金（取近1年平均）
avg_money = df_money['近1年'].dropna().mean()
channels.append({'产品': '货币基金(平均)', '年化收益率%': avg_money, '波动率%': 0.2, '最大回撤%': 0.0, '类型': '货基'})

# 4. 债券基金（计算历史收益和风险）
for code, name in bond_funds.items():
    df_nav = df_bonds[code].copy()
    # 列名统一处理
    if '单位净值' in df_nav.columns:
        nav_col = '单位净值'
        date_col = '净值日期'
    else:
        nav_col = [c for c in df_nav.columns if '净值' in c and '走势' not in c][0]
        date_col = df_nav.columns[0]
    
    df_nav[nav_col] = pd.to_numeric(df_nav[nav_col], errors='coerce')
    df_nav = df_nav.dropna(subset=[nav_col])
    
    if len(df_nav) < 10:
        print(f"  跳过 {name}：数据不足")
        continue

    # 计算日收益率
    df_nav['日收益率'] = df_nav[nav_col].pct_change()
    df_nav = df_nav.dropna()

    # 近3年年化收益率
    if len(df_nav) >= 750:  # 约3年交易日
        recent = df_nav.iloc[-750:]
    else:
        recent = df_nav
    
    if len(recent) < 2:
        print(f"  跳过 {name}：有效数据不足")
        continue

    total_return = (recent[nav_col].iloc[-1] / recent[nav_col].iloc[0] - 1) * 100
    years = len(recent) / 252
    annual_return = total_return / years if years > 0 else 0
    annual_vol = recent['日收益率'].std() * np.sqrt(252) * 100
    max_dd = ((recent[nav_col] / recent[nav_col].cummax()) - 1).min() * 100

    channels.append({'产品': name, '年化收益率%': annual_return, '波动率%': annual_vol, '最大回撤%': abs(max_dd), '类型': '债基'})

# 5. 黄金
df_gold['日期'] = pd.to_datetime(df_gold['日期'])
df_gold = df_gold.sort_values('日期')
df_gold_recent = df_gold[df_gold['日期'] >= '2022-01-01']
if len(df_gold_recent) > 0:
    gold_return = (df_gold_recent['收盘价'].iloc[-1] / df_gold_recent['收盘价'].iloc[0] - 1) * 100
    years_gold = len(df_gold_recent) / 252
    gold_annual = gold_return / years_gold if years_gold > 0 else 0
    df_gold_recent['日收益率'] = df_gold_recent['收盘价'].pct_change()
    gold_vol = df_gold_recent['日收益率'].std() * np.sqrt(252) * 100
    gold_dd = ((df_gold_recent['收盘价'] / df_gold_recent['收盘价'].cummax()) - 1).min() * 100
    channels.append({'产品': '黄金(AU0)', '年化收益率%': gold_annual, '波动率%': gold_vol, '最大回撤%': abs(gold_dd), '类型': '黄金'})

# 6. 银行理财（估算）
channels.append({'产品': '银行理财(固收类)', '年化收益率%': 2.5, '波动率%': 0.5, '最大回撤%': 1.0, '类型': '理财'})
channels.append({'产品': '大额存单(3年)', '年化收益率%': 1.8, '波动率%': 0.0, '最大回撤%': 0.0, '类型': '存款'})

df_channels = pd.DataFrame(channels)

# 绘制散点图
fig, ax = plt.subplots(figsize=(13, 8.5))

# 计算气泡大小：用平方根压缩极值差距，让比例更合理
# 回撤 ~0% → size≈80, 回撤 3% → size≈190, 回撤 10% → size≈300, 回撤 25% → size≈420
df_channels['气泡大小'] = np.sqrt(df_channels['最大回撤%'] + 0.3) * 80 + 60

colors = {'存款': '#E74C3C', '国债': '#3498DB', '货基': '#2ECC71', '债基': '#F39C12', '黄金': '#9B59B6', '理财': '#1ABC9C'}
for t in df_channels['类型'].unique():
    sub = df_channels[df_channels['类型'] == t]
    ax.scatter(sub['波动率%'], sub['年化收益率%'],
               s=sub['气泡大小'],
               c=colors.get(t, 'gray'), label=t, alpha=0.7, edgecolors='white', linewidth=1.2)

# 添加产品标签（用连接线避免标签重叠）
offsets = {
    '1年期定存': (14, 4),
    '大额存单(3年)': (14, 12),
    '货币基金(平均)': (12, -10),
    '10年期国债': (-14, 12),
    '2年期国债': (14, 6),
    '银行理财(固收类)': (14, -6),
    '黄金(AU0)': (-14, -10),
}
for _, row in df_channels.iterrows():
    ox, oy = offsets.get(row['产品'], (10, 6))
    ax.annotate(row['产品'], (row['波动率%'], row['年化收益率%']),
                textcoords="offset points", xytext=(ox, oy), fontsize=9, alpha=0.85,
                arrowprops=dict(arrowstyle='->', color='gray', alpha=0.4, lw=0.8))

# 添加1%存款基准线
ax.axhline(y=1.0, color='#E74C3C', linestyle='--', alpha=0.5, linewidth=1.5)
ax.text(ax.get_xlim()[1] * 0.95, 1.05, '1%存款线', fontsize=10, color='#E74C3C', ha='right')

ax.set_xlabel('年化波动率 (%)', fontsize=12)
ax.set_ylabel('年化收益率 (%)', fontsize=12)
ax.set_title('低风险理财渠道收益-风险全景图', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)

# ======= 双图例：左侧颜色图例 + 右侧尺寸图例 =======
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

# 移除默认图例，手动构建
color_handles = [Patch(facecolor=colors[t], alpha=0.7, edgecolor='white', label=t) for t in ['存款', '国债', '货基', '债基', '理财', '黄金']]
legend1 = ax.legend(handles=color_handles, title='资产类型', loc='lower right', fontsize=10, title_fontsize=11, framealpha=0.9)
ax.add_artist(legend1)

# 尺寸图例：选三个代表性回撤值
dd_levels = [1, 5, 15]
size_handles = []
for dd in dd_levels:
    size_val = np.sqrt(dd + 0.3) * 80 + 60
    size_handles.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='#888888',
                                markersize=np.sqrt(size_val / np.pi) * 2 * 0.7,
                                alpha=0.6, label=f'最大回撤 {dd}%'))

legend2 = ax.legend(handles=size_handles, title='气泡大小 = 最大回撤', loc='upper right',
                    fontsize=10, title_fontsize=11, framealpha=0.9, handletextpad=1.5)
ax.add_artist(legend2)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig4_risk_return_scatter.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图4 已保存")

# ===================== 图5：M2与存款增长趋势 =====================
fig, ax = plt.subplots(figsize=(14, 7))

df_m2['日期'] = pd.to_datetime(df_m2['月份'].str.replace('年', '-').str.replace('月份', ''), format='%Y-%m', errors='coerce')
df_m2 = df_m2.dropna(subset=['日期']).sort_values('日期')

ax.plot(df_m2['日期'], df_m2['货币和准货币(M2)-数量(亿元)'] / 10000, label='M2总量', linewidth=2, color='#3498DB')
ax.set_ylabel('M2总量 (万亿元)', fontsize=12, color='#3498DB')
ax.tick_params(axis='y', labelcolor='#3498DB')

ax2 = ax.twinx()
ax2.plot(df_m2['日期'], df_m2['货币和准货币(M2)-同比增长'], label='M2同比增速', linewidth=2, color='#E74C3C', linestyle='--')
ax2.set_ylabel('M2同比增速 (%)', fontsize=12, color='#E74C3C')
ax2.tick_params(axis='y', labelcolor='#E74C3C')

ax.set_xlabel('年份', fontsize=12)
ax.set_title('M2货币供应量与增速变化', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)

lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=11)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig5_m2_trend.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图5 已保存")

# ===================== 图6：黄金价格走势 =====================
fig, ax = plt.subplots(figsize=(14, 7))

df_gold_plot = df_gold[df_gold['日期'] >= '2020-01-01']
ax.plot(df_gold_plot['日期'], df_gold_plot['收盘价'], linewidth=2, color='#FFD700')
ax.fill_between(df_gold_plot['日期'], df_gold_plot['收盘价'], alpha=0.2, color='#FFD700')

ax.set_xlabel('年份', fontsize=12)
ax.set_ylabel('价格 (元/克)', fontsize=12)
ax.set_title('黄金价格走势（2020-2025）', fontsize=16, fontweight='bold')
ax.grid(True, alpha=0.3)

# 标注关键价格
max_price = df_gold_plot['收盘价'].max()
max_date = df_gold_plot.loc[df_gold_plot['收盘价'].idxmax(), '日期']
ax.annotate(f'最高点: {max_price:.0f}元/克',
            xy=(max_date, max_price),
            xytext=(max_date, max_price + 30),
            fontsize=10, color='#B8860B',
            arrowprops=dict(arrowstyle='->', color='#B8860B'))

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig6_gold_price.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图6 已保存")

# ===================== 图7：代表性产品净值走势对比 =====================
fig, ax = plt.subplots(figsize=(14, 7))

start_date = '2023-01-01'
for code, name in list(bond_funds.items())[:3]:
    df_nav = df_bonds[code].copy()
    if '单位净值' in df_nav.columns:
        nav_col = '单位净值'
        date_col = '净值日期'
    else:
        nav_col = [c for c in df_nav.columns if '净值' in c and '走势' not in c][0]
        date_col = df_nav.columns[0]
    df_nav[nav_col] = pd.to_numeric(df_nav[nav_col], errors='coerce')
    df_nav['日期'] = pd.to_datetime(df_nav[date_col])
    df_nav = df_nav.dropna(subset=['日期', nav_col])
    df_nav = df_nav[df_nav['日期'] >= start_date]

    if len(df_nav) > 10:
        normalized = df_nav[nav_col] / df_nav[nav_col].iloc[0] * 100
        ax.plot(df_nav['日期'], normalized, label=name, linewidth=2)

# 添加存款基准（直线）
ax.axhline(y=100, color='#E74C3C', linestyle='--', alpha=0.5, linewidth=1.5, label='100基准线')

ax.set_xlabel('日期', fontsize=12)
ax.set_ylabel('归一化净值 (起点=100)', fontsize=12)
ax.set_title('代表性债券基金净值走势对比（2023-2025）', fontsize=16, fontweight='bold')
ax.legend(loc='upper left', fontsize=11)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig7_bond_fund_nav.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图7 已保存")

# ===================== 图8：货币基金收益率分布 =====================
fig, ax = plt.subplots(figsize=(12, 6))

yields = df_money['近1年'].dropna()
ax.hist(yields, bins=30, color='#2ECC71', alpha=0.7, edgecolor='white')
ax.axvline(x=yields.mean(), color='#E74C3C', linestyle='--', linewidth=2, label=f'平均: {yields.mean():.2f}%')
ax.axvline(x=current_deposit, color='#3498DB', linestyle='--', linewidth=2, label=f'1年期定存: {current_deposit:.2f}%')

ax.set_xlabel('近1年年化收益率 (%)', fontsize=12)
ax.set_ylabel('基金数量', fontsize=12)
ax.set_title(f'货币基金近1年收益率分布（共{len(yields)}只）', fontsize=16, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, 'fig8_money_fund_yield_dist.png'), dpi=200, bbox_inches='tight')
plt.close()
print("图8 已保存")

print("\n所有图表生成完成！保存在 output/charts/")
