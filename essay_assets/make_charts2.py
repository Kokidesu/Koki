#!/usr/bin/env python3
"""New figures: (6) cross-prefecture correlation scatter, (3b) full 47-prefecture 2025 minimum wage.
All data verified from MHLW (FY2025 minimum wage table) and the 2022 Employment Status Survey (Table 2-3)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os

OUT = os.path.dirname(os.path.abspath(__file__))
NAVY="#1f3b63"; BLUE="#2e6da4"; TEAL="#2a9d8f"; RUST="#c0392b"; GOLD="#e0a93b"; GREY="#7f8c8d"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":11,"axes.titlesize":13,
                     "axes.titleweight":"bold","figure.dpi":150})

# prefecture: (mw2025, mw2024, nonreg2022%)
data = {
'Hokkaido':(1075,1010,34.3),'Aomori':(1029,953,29.1),'Iwate':(1031,952,29.7),'Miyagi':(1038,973,30.3),
'Akita':(1031,951,28.8),'Yamagata':(1032,955,26.8),'Fukushima':(1033,955,27.8),'Ibaraki':(1074,1005,31.8),
'Tochigi':(1068,1004,31.0),'Gunma':(1063,985,32.2),'Saitama':(1141,1078,33.5),'Chiba':(1140,1076,32.4),
'Tokyo':(1226,1163,28.0),'Kanagawa':(1225,1162,32.2),'Niigata':(1050,985,29.3),'Toyama':(1062,998,27.7),
'Ishikawa':(1054,984,29.2),'Fukui':(1053,984,28.1),'Yamanashi':(1052,988,31.4),'Nagano':(1061,998,30.0),
'Gifu':(1065,1001,32.7),'Shizuoka':(1097,1034,32.4),'Aichi':(1140,1077,32.1),'Mie':(1087,1023,33.4),
'Shiga':(1080,1017,35.0),'Kyoto':(1122,1058,34.2),'Osaka':(1177,1114,34.1),'Hyogo':(1116,1052,33.9),
'Nara':(1051,986,34.5),'Wakayama':(1045,980,30.4),'Tottori':(1030,957,29.2),'Shimane':(1033,962,30.4),
'Okayama':(1047,982,30.0),'Hiroshima':(1085,1020,31.2),'Yamaguchi':(1043,979,30.8),'Tokushima':(1046,980,26.6),
'Kagawa':(1036,970,28.8),'Ehime':(1033,956,29.0),'Kochi':(1023,952,28.3),'Fukuoka':(1057,992,34.2),
'Saga':(1030,956,30.5),'Nagasaki':(1031,953,32.2),'Kumamoto':(1034,952,29.9),'Oita':(1035,954,29.6),
'Miyazaki':(1023,952,30.7),'Kagoshima':(1026,953,31.6),'Okinawa':(1023,952,33.4),
}
names=list(data.keys())
mw25=np.array([data[n][0] for n in names]); mw24=np.array([data[n][1] for n in names]); nr=np.array([data[n][2] for n in names])
r=np.corrcoef(mw24,nr)[0,1]; b,a=np.polyfit(mw24,nr,1)

# ---------- FIGURE 6: correlation scatter ----------
fig,ax=plt.subplots(figsize=(8.6,5.4))
ax.scatter(mw24,nr,s=42,color=BLUE,alpha=0.8,edgecolor="white",zorder=3)
xs=np.linspace(mw24.min()-5,mw24.max()+5,100)
ax.plot(xs,b*xs+a,color=RUST,lw=2,zorder=2,label=f"OLS fit (r = {r:.2f}, R² = {r**2:.2f})")
label_these=["Tokyo","Osaka","Kanagawa","Aichi","Akita","Okinawa","Toyama","Yamagata","Shiga","Nara","Tokushima","Kochi"]
for n in label_these:
    x,y=data[n][1],data[n][2]
    dx,dy=(6,0.12)
    ax.annotate(n,(x,y),xytext=(x+dx,y+dy),fontsize=8.2,color="#333")
ax.set_title("Figure 6. Cross-Prefecture Correlation: Minimum Wage vs. Part-Time Employment")
ax.set_xlabel("Prefectural minimum wage, 2024 (¥/hour)")
ax.set_ylabel("Non-regular share of workers, 2022 (%)")
ax.grid(color="#ececec",lw=0.8); ax.set_axisbelow(True)
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.legend(loc="upper left",frameon=False,fontsize=10)
fig.text(0.125,-0.02,"Sources: MHLW minimum-wage table (2024); 2022 Employment Status Survey, Table 2-3 (n = 47 prefectures).",
         fontsize=8,color=GREY)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig6_correlation.png"),bbox_inches="tight",facecolor="white"); plt.close(fig)

# ---------- FIGURE 3 (replace): all 47 prefectures, 2025 ----------
order=np.argsort(mw25)
nn=[names[i] for i in order]; vv=mw25[order]
fig,ax=plt.subplots(figsize=(8.4,9.2))
colors=[RUST if v==vv.max() else (NAVY if v==vv.min() else BLUE) for v in vv]
ax.barh(nn,vv,color=colors,edgecolor="white",height=0.74)
ax.axvline(1121,color=GOLD,ls="--",lw=1.4)
ax.text(1121,-1.3,"National avg ¥1,121",color="#a67c1a",fontsize=8.5,ha="center")
for i,v in enumerate(vv):
    ax.text(v+3,i,f"{v}",va="center",fontsize=7.6,color="#333")
ax.set_title("Figure 3. Hourly Minimum Wage, All 47 Prefectures, 2025")
ax.set_xlabel("Minimum wage (¥ per hour)")
ax.set_xlim(1000,1245)
ax.tick_params(axis="y",labelsize=8)
ax.grid(axis="x",color="#ececec",lw=0.8); ax.set_axisbelow(True)
for s in ("top","right"): ax.spines[s].set_visible(False)
fig.text(0.125,-0.012,"Source: MHLW, FY2025 regional minimum wage table. Spread: Tokyo ¥1,226 vs. Kochi/Miyazaki/Okinawa ¥1,023.",
         fontsize=8,color=GREY)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig3_prefectural_dispersion.png"),bbox_inches="tight",facecolor="white"); plt.close(fig)

print("Wrote fig6_correlation.png and updated fig3 (full 47, 2025). r=%.3f, R2=%.3f"%(r,r**2))
