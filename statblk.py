#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-
"""
Gather disk and partition info for block devices (Linux and macOS).

Run embedded doctests::

    python -m doctest statblk.py -v
"""
import argparse
import os
import re
import shutil
import socket
import stat
import sys
import threading
import time
import traceback
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 57):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE$ig8-O-i5'i9DjZ(gR+RLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%NdN`;%MLm
ps(uYZLt9N^(d>j;?gF2fq.JS8E^d=!D`Sq$Gt&.k_&Jr(6<fc-."_L#%?6QoJ:i3GQHb>?A/=XqGZdH'Nu>j"g6i-cqUX1Al)9;U'hMS[PsbB-tdCiI
VVRN65*?GL<kIO7Z/j:-TJ#--6!gZ@"9F@Y4QIP8RIA*-bdk,+]#OSpqE:>dQXWo%Vq.P6Z$)MWFf[k`LRT2[,*GhHZ+.Lg1@2O[<[B*K-.'N:N8H<<,
&E1(pirr)5m!#H$,j*ACTEldRI5YNJ%bV?H%V$;hdcSHb_`4D:n9m6o6@reHo[D[;$.gm!9.Uh1`p@H#R:?pqY4dp,biP?jQA8q`8J7=e]+2fTO:g:r5
JD/Ok+BP:ZNg8Ufpp3_R\<^ssZ3(N!N1mi^M3B+b</b`/fF4E#P't""3\3U3n+KsNdn[1$*@<O#[P9\R2mZ*;$KpQ;XhrMlS-FUZb`eQ,TOC-C/_K(@j
PS&3r><Ohgcbp[!B!$O+V0s6Q*L=G+)9sZT4"^I33/EHdeWoqeM1AFkeq;a9;_(1$pohE.-O0H8Z%ig;DbR7sJfs!6,df=,m"Yh6+Jl[7)fnV89KQCa>
3[_N#]9:M5PP]W7s"2cp4i!CBq:"AATg$E%1S_/rL2m-6XXi*5k$<V/Yl0R,8?)[&/2ejCJu^?Ke67`g1/<jVKg#j$PTRGgQRs98%nJ+NOUbn%8]ad--
ma!bMPQn5/M?bHbm%ifkhBrKVu?^K?$#B(Q*SoIg<Q'Ep-(4HWNA:g+_Ep)/;T4KS)ir9$hSAWc><up/R]#U*>W^IO-LN`^hTa7P9RK)SF*GFNOdX]8N
/3(.`NaL!NX"O=j=KrM=&*GG^]>H)OgF5+nd:$R=u[RHTCZr80Wos5]#U>WKDXm)SB:h)@`^G9KKs1kZ,umF0>FH75KKO:o8.!F[3Y\P@CTTm/L6/[s'
u"E#+Fki,nQBnoR:<*R3S\M.hRaNu<1Qn9Q"GR?$DaM2)YP5_$gXTNCLb9h;V]Q)uj*&7Cg0@nC5;HH#Q?Z>^&$OrnWq^I)5!>1tE.Te&0:\Iej]Dh5X
7N_Rl@-.K(fruakhuWDsa8IdP'_@YbhX]9qQ0Y#rQ#HINO"TAdjSMr,/o\KsR%%?K]U#BoRMp8#;m:cpKE&%(Y'eI<iK]u@Nek4@:J`[]UquS2q*eEd(
*aF,^,3R-82%b?3OS?55]1l@Ul6GSgVDT/$BYW0)[l7+<G3aNDJ/890F*3N5X?K6;A7KGmqEDA]q`W0`SQ13&Rh`Ifd-7W.PXjR7.kh3h):5B37kA%Q]
8Q!SUPlN7G_pQU`F5F.8K5I[L"YMfjrFiC?"ca.@s7*(oXDMlnY#iDggDune[gu3-)ceAVTpPE8=IMK]72IZAu?-.p8n5j!17AK&a0[R_:(:Hcm7PG3n
1;H4jTGSG/g6]jcta<;LqQ_b=Rk.kc;.o7,IEn<1LF]lRMHJOjG8/,LA*r'1&+?:RR-06Su9Z1`CRIK?9q)%u.q]'L,^_g(LQ,#@<C`AY1XJ0"jb(=aX
aR7M1BTS.EpY(#;@rD?DqA7[[C+\l1bIGp-h!KpG^ZVl0U:M*IiX\'(jHd<9YPr:B6D/#sDI:-^k%f=*cj^;bTEV55l98-^51[nLaN%1'=0U8J<55Z+Q
rJ=/keu5:`$C<ZaUq'U2oSa+18d<m!DR%Qn!rQ[cH)#"gXj^qmUb6Z`ntY[k[H,*j\LYSas*C)4XkIA+,r"QRbUQ:+m+_9!cU(/]Ohu0U/:nIFDrs/$:
>#",l6Wk@kSUH]\p"EbU%8u%E)O"dArh,n43^%78FAo',d00'%:@FW%,o+PQ<oXM6L_7!o@m*ag$GuK^O'fq6aaA/>Z1n^a9)/60;s@Ns3HV07YtsnUX
\XXC7XVHW_3X+70L<'8]=2<aTa/!HDqqKFk(dVj?(6\FrlNe<=0,R"s/$C`%I28?q]N?"m`#RRr'f9RkD2u%:nm88\hL%9J3D_-M;t1km!4V)m7J&f-^
17lY1n6mOCl!7n.&I4N%h'8XV1HVY"WAJU@pT<>n9%j36bVYU->KNreqbgilGDiV>.lK,b3I\]ir%IRl0CFlO![-1RTDI"kgE1g!9Q0o_T1J8pI##II4
43VrP&m[u]LZn4`Hm&/^a32Lhucc7c4&o:qKKPC"73.[uh5O4$-,c66.-J2CLi``S7Q=.uiS%dXnqupaC!g-IJ*HIQZ1H_su-f_+uUYH3(k0="X4>U9D
^([WH%oRg9I1!pra3Za-!(TeWB4A"\Q^3bj4&9p+*4aM"Kb!<NeI"40.4.N^S%TR,(u:Z-d?=in*TR$+eD.tp!d"j5R3VVGFqI8o7EW75ai20WdW'>FT
;\1mVWYJ2%U_!/IKg85Y[K/3gY`&Sei4=_K>c9HBjQ^)l)'Lqfp22Q7984hrh(t)WC:$a'T=)Yp`3ehdS_N4B%IbK+#eW1ousKsUfE<@>YpJGME"95kF
0qjcTb\fJAVT]#?'hW1hS@<A$pb?k0t<n70P;_RlI#lNY!?qa*hqK)nel\$_n%fdfpg6SU1;'G=4ntjuk[Kk_%skR=sUCrldB*R_V.M?@RC9jS!fN*Po
@$6n=u7EJ5q@_R4'2M&gK<.7<:1;,(:V&'&T_[_!f!dTTZ@,FRnN@FkVW:D*ZE-IF]LeH['8kj6Og";E=VQrf7c^W;>?mceI;ejPN!0h-/l$u6\P3Zga
Q^Q$W6n):&tL[M&Sr\)YL>k`8hlk@]Kepb[P8BE`s.,oXnc!UWs[c>dMV?qYjA:MV*41?'+jU=PFR&EHb(KP<j)*osOG#T\6:"F_H@psl_jUF:qH194%
8NFGG>VQChPO/*cA$?0"J8CV[ZAO:jU8;7g_,TI97uF5#<Dq1EkO*tQ^<$02@ICVOn@`XGI^2T,?D-,T-ACteP6OigQr,PS6;="m?$pm.0D2n#o[U<Rj
rg1reUut_nLBU:$qM<noHUZ^(`LMb&&&@G8MU?ZKB@b5J./__(@8)3aFerC8N_3^[db.r)'jWV'Q`^"+`\8J]rU+?Qb*>HCBXId[!]Rl7][)XZ2jsL()
*>CY[bjMjLHmJB9@FnND#k90kRU?pm*?-:KQg@"NGtGf68CTKS=)&kpd(Hm^Jo`k'5>u]R=Y=Y,/C*>lqK&r:Rr9Ic2\tYqg]8NQQ"70U@:+=#8B[CLr
(8Qg?h^RZrHrd@C]f:-'XAbRkuA:NLhORhZ2MYNe40.+D=QKt3CHR'&O#n)k&m21jU_dKD6iptKBJE4FAGfEb)?[=&)L&-h"^%e/WFbm75"_kap<UH2F
$=)<+hL%>L;fWdcTflL*Z_EU1PqXURi"D]SG!C.#jl)Fk-bN4GuoXa+;oR]\Z.bct.f;W$Y[Uq2`lsh#8e]#TNK[Y<4Z#XFR$Ro;uC_J[5:@J7:G*,Qp
c<V.[hK*4oIGBcb7R@u<To6K-['/Yh5oC;6=PmI.&r1(*&"$%@BA_O"fPLdUe'2K;)%,tRB8Ir2dB1-VOJi?4BY^bjZM,nLW!?^I^^aadDRI!7l<fU<j
+1_l;qEtCrCC_3VOtXB6G[/DYUBIZq!e8bNY?#@G*H`L$F>$H!a]Co=DT3/!q)SK@C#'*!,G6^dnuNP7<#fL(9M/>8,64q2ZtqtW5H*AhRl=Ur$^9t7T
*+8?Lsu;^\KOk=o[@acks)dKf,r%hm<AC;c;34ki@Md+^M28BD)j[@.$Ag;CH!305Yr^8i0IFm)\aRF-GSq-P4ch&F2_4X),=n)s\2+)KO/4p1?SaW2I
%TO$<Puo^8VXBOY!8m5r#/46h?%V9dX[1,,8eDurUo"O$k8%TXYP(sEYkC@LiHG94\,%JW:f,)Be[aBbYCBQ_b&s0!K,X-UbgDl&`s;0H+iGbmO7pSP4
+B[7A6X_:[N"%c$:Bk1i0pgK<$&0$i4B2odQUuI$)+96Wo(;'sEMA=QJ8q-bScAm@W]K^]nDtp.1&D3.4Y1Eia/+^!F>?qRnICiNk7l.<1W03Hah\C/#
l9O8/FlIcpRrgqD`fp2P+PV!@LpOi7L1(QI%h2&=D',]OE?'?QRj&G"fZhKn-,I2A_a(ds@PfHU"XMuN+cb;eIq_M3ZW[l*6$Z6pQJa@`!&]9E!e@PTb
pR[:=ab$,EpUcPaYV22Pk`B!Q_AOJJmoa??laIe#UsbUBK`@(Z20Ra52qABD_OVCc^h91)iZe2+J!e4S_"gXr!-=hW7WM^'JiB4W0KQlHhVur5WFd'5p
PS4Q=<_o@tqme_X:-.:cN@SU2m`:kTM/YjX/&f+Ef]!-C#KF3^sulYG,b=n7VHGcdQc6+D9V`\#LDcje24KoZn?;LBG/<jr<1'bTpfkV0>[dOd?/;[^S
:YX1?:d=iNK549n,9nu=KI.?P51-D%.,45jjgY0_NP!)\`6Z5(U%?o&i%qM#<+<m/:3Ue1@G5A0K+""#(H*?G1"B*EX\^Q7K_NM>#G@3^@l,*RfIKqhF
K&-r[4#%L<HqdIA"mjgRB]Etl=Wo<X"iAts):QF!kqSX/dj_/"C7^5fol\K_h2W@#4A9R7h#mVTup'+=gEl2F_<&BY^<6a"?e$n\.pSJ9$NdpB[p!PQo
X?!Y7K)2kcP<D,k[RR;Yn\q=&-n`hZV$Q`2#*Q94Mg;)=!i,ut@8#AtNgEHKe,CQ#Nrip-!8TZO-<sd"iTjqV"G7K<>ZN=u;5mc/TTl/#Sj95LHsB$WF
=R!h!<,0SIc3/.i]#LV=e`^iOA[IF]sh7)LGXm[Ir]Y*34Uof\k$O)d)t%;H%^Da(DP%>W-)=1!l0jA8!NliA_S]LW3[!&">;/;R7R+O^\F/X?Q0?@d%
trUO<Xq4eKB;a(1#.0qV7^Hb)t53C4mAa$"IYuD&mFBAm=Z7T/&;p:.HF/H0<((YAE<QjAG.7D'lC\NI5bRBO#)6OGMICY6@99J+*uA]@q(m%""3)8$2
t/:g5!a#]s*2hdC_ecWF&Y`mnE1K\*=o*FfnaEd"2MAepg9&BOp5JlAgfQAt!j$cmQoLY&Dc+IZ=7N7EkKL9-kB)<3(kbg%E9Ed1,kWdh]/pOWk[&83:
b;3o1i:YqN</iBKU,V(>U&Dke#&l&kDN2SO5<(MH3fqI3EDHO(G@Fib!'*N:8VR3&I2L.=n@)Q=cQ*q%Jk1.01[MS7U!Ga[)Xkc"oE0OlOmG`htDT"PY
_BChXVhNsu$1RTTj-2**Rm/e`@KD%Go0bhW0uUpf%.IQ+-7k;!IfEMW[gLN^N,h;D?-&^N&+e"em;*a*a1B)nEJ&3J;X\>Pm)hpn8"FN`PDa?[<Met>g
M,Jk=K(>.C:9$I<c=rl:"K9%^G<:cp&\7cMu((OY5=h3&EXe3m,MB0V/`#Nr"HZJE[&)ldFuN)UqSo['=T70>EYKr`=o$L?o^RmKZpQ#gf(I1Ck\aT)s
olp3?i,r&F1,eX?)?-S%0or:$A'!Tb9;0-)i+7MrANK`j2M__UXA6BX]ppQRmtK_1*M:$70c0`;o@^8+:mX0D3jJ_26-4M%>'pm9([L27;mui>kE;m#>
mql4`#Wl:h<?/n^H,#[<Ymft%E@eI)T&.pt=R_o/M_jqlar'qLaF9-,ooC@2bkk?:nNn=$+m:F&88rGpJC>+dX$d=&nXf3]=WN5n#dRlH9jBFWRkQ@)X
N*4q,NHDK1<c0V06emd95_J)kEL!VFB]k96R@eYhEju:07/kX>k?e+QT]8Wh&b$10p%kR8c0o0anS\Mmnr:Gj^l%l8ue-&kjK*,+]f+H;gN5eF+A%!?O
rCo)X#YM/AWan!YKB5!NI>!YG15.mr!/4Sb/SBYqo>`Ek"3YE\>>b1iirP"pX:_2LW=C@cm*/><:LcoqLC$b.K%(oHpWV9(!h6A7#HGWYh%^=YDIgi,m
b*hT/GR>98u)/Ek[$pamr"5NpCb5eE64j@JD18/\<7mLUEa*ji@G#aB$gRB=Ddj?\>C3nG#Yd>a1p>gHdF2]%PG%RGO1,K7s$\!WFAgR`J("Z%h%N*`Q
UNk7NHJJj>lu_>nC)hmg]qXckYTF#:d#Be[]GS)a[RPcm7_=dM(+/<sYI:X8qk1-.q,b\u>aMBI`V\1<[AGa`(U3kXT)Y[)N.[$I_[A<_P-`9aaT$Lf,
mp0quDXB][rM]<.h-CuuaI&>K"CC&-4m1lWM+4*91H")Ds6AiI&WNrg5_@:mLI$@Y?\Z@'?S>X'>W1oS[l\nW'$rH1"6Q8u]:g_W:HNP&?DX@c[t/^>A
Tq)E9V_*)HEP"V5g'-.-*Y];Nl]^hW*Y1Ze&[4!tgHo>=OlPKh2^Qiap99=J[>aXJrf=kPkInEIb1TU)$5*@M3Rj[]':Pc>[J@`a)BGj5PBmtK"._=Ea
XpsPBVb,<Zb'bF/2SL3_r0jU>R?C_&T4%):q+p0]qVjgT(r?;kYXWSAdfRV1"tT)-/qK%[SuV8@+'Y1q,JJj\p&dD357LS^'Mh.*guHQZ59?IM^Y?MFX
bE4a2***HW72g`,m&q0,/S!mR[\4CYb++9gGo[1!'SbD9'eO$9+R:DGcXl/)iAL9Bg82#!YXb)I5&L$;1rds4_M7>j[#6p3NLl2[J]r>2U_oiTQN#T9M
HVkC-0*W?Q\.G\\m+!W.k$o#U"n4lODUXbIoSu%JdKRXTq:Y"0'"8cQTsqVRn4'oT?4L,2@T>+?Agg*J2ID!2-$#"-D>KIp$3/V<jE#X.lPBch^#S;3*
KOJBR+i9:f1*+Q"jrjCF*JZf-Sf$Kg,7m?0<<W#L-U+g9sh]qt,Y8i8@!ZAt!rA*1.>L/>;cmF#P8oE6!.gH1SO;13YP)Tb0DcaE$eQRu)cKe>Ve%>eW
U9($W5W72BHr+QVb$&_n(4*7t>_E"EiRR"nKeKol;6tHRiml-q)R%e\u@C6$+P`Qi%Mg1sp"oFRXKQ@1KU/(.M*_i&7?'#g<9*mhn#[>X,U7"HAm2eFM
ccN&5l\]*[g%MO3JK&$%6ML%CqlbBlhUtlGT6].gGZ57-6mkI<5X7$`5W5(Xr)+ps[(n*gh8i@3+@*d,.Up=55o,7udd$+!cp*Z8Uk%<(GejXf!fC<]q
ccX7l_og:DZn5NcrfJ03f"mu:>n9%q1mrk]bYZg,LI2;(8/bkb#cI!dd5HlHH&oAXK^NqF$_d%E340mK1S!(P5<"?#Z"9fH"1?9F%1[cB]s+)H2IMX!&
NB&G"qR!%r^+I4P([&M<<-n6NTrj[s8iGm3$fG.4'0:iGU,*0k;FXLUfS=nVWs1#.+S:=MHS.,<&N=7oaA7\<-<m'TYp+5*J_?,kX[<Oc)3Uo1H\iZ84
0H>7NSD>4Z$'0*-rD/5a?i4!jajUrk^:G>;WmVc2Gpc1qO$7<4YKkFJn2Q+/j3PutlK^uS9"AA]s,2\i]?K[Ts7^t[-f*0V$$K!2Z$Tcj>:O)b=YPYMo
lc*LrRk9Rk>S''[ME:q3Qddj+RhBJc7C8a<eo5glGnqnI!7F/WZ-=PqS6=uadd=K"*MXVcH=%7Q#pT4K&CG;6C7CbJ?i)iR49?*r+J4"[T?U@V?9(LXn
GTdlejCHIrQAk@3i_3')XXlGkH&Wc$=s%ie#fA969^N=[n6M(b]rA_k\B29XW<Hr4:X)Y3Yin1C#i!=/YPCpM#jOaB,6R2#fI`%IF:lrb`:$orNPT9X=
3<;CgJu?)"#0Dr)bGOY89.J'(t[og:K'k-c21SXii[(IUOAl+VGlUjI'<9b$!Bk6/V'gt].0gb.;s-]Tfa$T54-Z)=5R5'522aA>O':QcH.PiY"&OW`k
(tn;Z8uK!BHI^op<J'),mu=W,;lq2`XM3kZ)OB;]'sV%#Eql0Uh>'.TJ";l_*4M[1ZNt7-l3>@BCjda0X4k,J@Su7KfJSY2O7K)Jb%5S6a:u:(eXg^)9
He6E>EF'M6`=-#NlO%K\W*1=]IG"#i+0N8!T3P7HA#X/i1_)*-NP6+!:,8RL-$"IereO_M2_QeZhH1A0qhHa?b+=IhjU,$.JcM+.*Z7EYHgcouh07oBW
%&VH4X$b>`[oAZ`p<42Oo(43r;A@tj:DW^NTLNW9\Oh:N.X+I[tCja-?Fu]Y:`B0E>;2-+qd5tkELS+JeR;R\*eh4]RnZ[o=F'[`tSL(6!+3V?#p7jt2
8jJ7@ajYZ!7"T=u<Pa@3O9E[>HduQR8`E[$q3+@KPIlnco<k,pW"-CPA27kC]SR/V?oX,TQLs*qC<E>9M2eBs+^WKhC/Kg4ZK92U#g'[c\8ArPV50B<B
jFSc:3s6ZDR]18Hf]IYk@f"*8-#Sb[2r1e.32pVFND.YN0.D!Q5lUkA!hdl*G.]KGQ"$fforNHO'P:\m)W!0n4F7@JoX.d2#nfJAm,IXjHJ\(Q%keGj]
hQ*,,S+u;+b0T;3YI9B<AN/\tKRjM3NuJW)c&"_Nh\eIZo'2n8!2Zb4@HEb,tq/A+>sgf^mr$A4_aWZq,cBcI`0tQYArR4,7\ma6=1piGgLl18t^MA+9
'GhS]C\FP[9U;"c_=n?,TF5o]f<!<F%8Ys0bkpnqG/>O^k:h_=l,U9eNgnJYZ#%K$2>W+jXeJYB%8VOQQ'!_OZQKWB4SRAI,>l)c6KoaKY,Rdk8RH@/"
h-?J_+2e"dG7')hH+m$;d?:L=@Y!NaFKNCIoTY:rkJP@"7Qq'?h??3qmW1C-=E4-cq"B$[L4g^eN=@btE<pB=@B-m/b>B1#0-TB=]Q7!>NSG5pFe.oQG
l8dm([%kZU?+R;tFV8Tu:?Ms_ZV8AqHArnVotmI<LkE.O_JQ0AQ)q]ps%gXup%WqFI8UcbJF$fVFMZn"lp[#lMcTki-UM)K)kfZgFg)u,,.41V<k"036
X3K"16&!-*81:\&&@.c&t"M.f6&;N"T=:NG$>l\MKla]]:YA??+_*r(5%i,?\$`-L4`EnYS8("%S4Li8lro+Ipt850\VESpu_4J/X#PRKmH8@S[)em&u
peYP/Yb08^C8VJP&*oE;^&7$XBqGX(R]Uf:,4bZ34:L<idG8#L$-(=Hl*p]?Y5\HU+RL2uB75"kc*5#DHQ4\#RpHZH1PKDJ[M_eg+XKW-!RsH@]c&::I
?m1%VBM[4a;g?4,;!;Y3es["Oq2mlb5C`a4E?ACJDWSecSD)H3L2$!+Z/*XB)4`D@"Bpb0)dd9sj4P'RJ770A;RV44LG&Q_3a[.2Ejb.T!3PIG6K1T[F
W#41PHZ#cK-:)pHi#/'//?_AHodBWM1<\2+1V\.;[_;4Lhm9TN?GjGCm(IsBP/X$)?,.biKfcAVE\t(W[0Vbo(e\t7WQ4^lhp'CmHQFLJ!7'be%cDRfs
r=+s&%Fc7G2HhZ<Imi\H"*AA[,/no`?tg^OTIY4q^%a.5'E:uR&hV#^da@^8Ee(=-];VT1Ceq`(GlE-V$T%uL,FJ?QMGZM(P(n;XKg3M]9jI;O_kGVWn
_HDlKIja$C1fS!$VY+a+:%,$\oBf+rUH<!2qKp?geW=(O(%A@Sm.`g67CP1ci.BY&Ao?>(ngpb#UG<Sp]'iU`goJ$`cIct:&f!SF!!s!0:q)?>?C@RpB
D#'64hK7(lJh$JjYERjBsYdAFp=&cVh)tgkC_Sr\lsLrMS__N1'?^bT!_"bcf-lQ@+!1/dIccgF+HrE@W\pRUM7li2/l)(Q/)rf<EI(rUjjO[4Cam?kh
a-R7_`t%6_anG#i!7ZlQ'Uo6;W,C1XB>GPgC;kJ=f]+R-ur9i.9^&>M:U0^`9-GAa$E#K'.*h&L='l^]t48_kkG@pupQ;-sB21A#BLR0mGtm1pLVhQ&D
W#2+:BCi/UkX8JaK%*HQo"#RnHb:>*?`&!AgVT&Eq0c'i&%4TWLX;_OWP*W>4l&f&T570mumI=R!n$hkhQ6RDR&4fi(4cEj<'`aEjbBIRFY;]N9&p^'"
/]'6Zg$ZC#M\?WglCAC(c+>)^?O@SXRTAtE!!@#*k$=ulmrD6G:GX<*#<H/"TDXYAI!7m_?S[*B[oNsKegJ&^:/+H_a9$$dA\V;*WQsDJmT5m:,g`9rZ
N)W)RQASES4hhS9b1AqF!7l9Bh68;2,)fb<KmN.#Se:pK=^+@]BnRW<-P>)d$@+1ikN\Z;Cg#YFuMiLZ'MQ*>MoW\PDJ45C/qbkErP,]9c+=C$[p66kB
cYE?:]mif9&jtjT-^.[WZ4KC]?SD1[[4#.D&bu6ol`9K!<>ojX-#?,Y*62hmj!TcfX@kc7%SNJ^1KC]PK^Mb>BFe%)k*kkS'W.J-N?<3-_(W%&qE>:(#
2G<8@6\cY8+.:&GaP7W(GEGiVih28MYh2iToA!d:)2%9'j/:jo?H4rn+G-08nLP;q=D?(\jCq3J^k1/f>nj\?mGR4^DDTAS&;N2ID@pF$!"Tm3FMI83V
!D=!CZA@!tf#_%fa?2+:#Iu#9bej%1q<0sMZrZW#jD&7%u^S.bIPf6MP*I/Ta:TKA$>r]35>SLt.hS8Mbp<M7G@KAYG!h>n%Y:kk=Ma5lA"c.NE&VSuJ
]&raa[-_+pdRO8@IN^MqQqo^q!$S3&c9m(CpqoNoi\0>VoH"536KVN"]MgnuXs<(%al523nGH1::)''OLL0JpDde4qIb7c/>cI-HCb4<YU9Id0FZ&e9h
Iu-p?Qt,gDeT4lS^7gLTTiOuNaUQd[ErW2V<kMV7[:ah:e$9k`(hg+o2P"ePpn%2VoX3n;*6u1=5]ZHbg`4ior6\L+Cr[^.'bf:7I&qg_m\q;RsTtk?6
*G.kqm9FM0qY_iO3N_WQcq&dhaA+'b\6j0S")q+,o=5D3Sb4?HLea?.fDtb.M;KW3hG7\qgQO;&p3k@90(u%36QS\)k0WdW,;^X]7?CFZ0\lP5'(%5i,
\MP\e[g?Z%0*,*P_bCpTWB#Ka.JBFpP<&gJVfWR*r<!mE^be\@r?:\fftk:DYhPk0(M9:p$1f)2)L;,%E+b,bK3UG&30SW-?:k3[?X8YWI05BdBq:=!A
MH7UrkXa\XHqj0`tIMDP48Nq#`0C<p.-5+s%<4;d+cClh0EVdiq?ZJM\N/sM=Bbs4prJN&L1J7;eqV&A-"[:"YCp^FP4l7u[mE-.P>X=;d'4PlD2#%/#
)V9OB`$b*uS/6]8b)D1aHq**BPWskgSsPC-X[:Zs<k\RcO#F3siAeOee4.2'oZJ4R/Th:;5hN-_Ou?8,kg2L#jZg-n&OsV/DVJ(:s+Q6\gKuV5DKeHLK
W7,6r@AinLX'*?*Q-^I/Af'5Ys*W-S#=3Tr+fjj.['Qr[aNFc;I+[<SEAEW781D-CMS.]KE3qUP_V?Ip_J->P4Wk[G6o$\R@]9X)FFt&qCK&SQfjU0D0
Dp!-gn7W%V'9U<aqOW!CHkSnFVN7<L#fFO1u0[4hFLt^c-(_j6_%h,<Y[e,Z]J6Dk=,(XjH!a!IjhZ(nJ/1I-4f`_`<LgrPIZ&gRB'85ToYjoF.YLrU4
o90n2V#fq-'u>7S9s=r_gmTMR@6P<k$?Y,N_UOolrrYB=OhD/kn!P_d9T<Em;EZNtq9,p,>SJ:Jcr'kW01)EDOF5CZk;3GFqX<2RND8\Z17[R,l46qSo
WI#g?$dpFmDeiNMJ:0,Tf<!-3XXh%6FnUHq<<"E%SIfRm#CmL$f_?+,W*KTpt;jqO!N=CuKYQo"-%*Tq@D-25^KMu;[=]7E?g];NrB(0s@>>-Q6Pe_2l
mgn3.N3P=4a8l/"UfGHi*ohI@)"mL-i%o]!qrTNW+-,?7K\?ISH$Rf])GmCSgO_>L=$Y/ZJp,i.o83qAPM<4NY>7:O>j;iE]&dGX_f<ii6/1#K<M'G7F
sRl?`A_NN^O<hMfF:uIQdF9R/"u11`'APH.Br>No2h>q;7W%A&;1cCNt+.W0k.u(dg30.6#jg20i:>N;P(8_a.J[V[$hP-X4kP?(V#TQ%<<cl8Ckj3Jd
$DHEO<QOnI.Pk3!f+l=@q[9O\ncIk+/&DR#'S14CuVn%(L-u?VCARV?/]0gMsn/KPd@#p*r1b](_cS%no8J-9)<k%;3IpN2=hURTD"qEtO+QoVl\>\Wa
g&A-IsFN%HVRZI(9bh<Em%M%Gs&ghL%):?&-6X>q?6BRs$;p5HR1CZeI"?oVS,M+:PQ!OT33;iicd/i]4=FlEI!*YEAX#=<g]Q>1WmR=&=j;pF`c*]Z_
>/2*0I?%!=&@=46&$D;E%%`Ic2q,YHd7^S_>JYP?:[m')7U:s%9eioG4Y(XQ/`_bSN:sbEC?.jG/[RG\miRkgHo@^,#m0_kOS0<=mq+=[o/e+biETD*L
K#J]%XG=]<3,`/ELs81,?Es)H8$c`\BLKbbEQ1D6Z2Y'DeXq7PXVF_2^W<4qqn0K0]l8iO&I/o=mOk9:Zser3*W*Yo4Ld8,!gAsh5E64@ao*I?CI)eIc
jtnNPEW"QdKi-m'eM2LkV1l44:UmA,#3VJQj$hHZ$mT]8uR:,m,CV4Ya[)`U8eu\0p+'K4TAjAs&89[DY;Sc(:Fl/Ks,lI'j\a[#[dVNL9Bg;F`E^KG.
K9G8l..l&%(_Uh?]%UJqV]7SZ=YX#q+Z%r\*1D34I:Am@6YEOk^Ip/pXNa.n$(lkmi.0@>DPk89(M$b9H>([B)IoUK"g%5/VI@!OR/rG<LGeLF\B'?NQ
%,c]A!m&[Ou@/3&71-Vo,(+U3/lY\&nc9j@OW`"jO$+,N.cltdL=E9c5%?K:o$[="I\l88WQN,U25BMe/f$-nOOmiE_4fFo>i_)4p-=M1<hC+.[,%;5a
gG_J)"rf^csFkDCki#1h$RSdub*d[;hdg(X-Ydj@o$Nu92Q+hBu%Q!+.+'a&YF(F[!Y1l1DG"Y]#YGffkD$O>=dk0q\1Kr*Pmujb%ms"[l^t=,/aohFh
K-npQF_4Y2W'[^(%#$^KkXS<O56AG<Hf;:sS\?&[.MMTXh"M85;50A-dY:-'qJQEp?9AV(XYV&G#Kbb$6m^:aW(m^nJS[E)&=*JHj)CChReTnZ\[>7Qe
7cMeCWP*Xg@6U&[)`a.QC:CPPUp@-[AWHR!k:Ot.)i_nL%%R7V:2ZcC+[;r%:q"r5Z8p4)0gN4>>tUFr^F]TN&?kWLUurro:<D^W4Fc;K>TB:'GTsJ]I
Qg1#\M[b;O1=NS\&$0cf/\,1M"4SW!Q*F-YuR5#;*l+->;f8maBM6)^uu9\\kT(Va'Gf]b=e:Rd(:81M`GpGH]<P286iG^poD;=&!L*m*!?]Pc%JMRR2
uj<C-fgokjVPo&`P4e1[RmKcmV+6:H!C!JSTa0&L\-_k4&-qVn,9()pOKE1!7pYYr?"2n)T:Mn*`a`\VC\h#?"r@<_5fT5)MZ+aYEI]1Z-s/d;U9ZrOE
u&_ql%hS3\.b*'&10D<_W2.qp4A@1#fHA)jJEibS76;gMo$>DbO9V\&,i(^^9$SC@I)o.9dSk,E2T3mT+r:2#AmTW04`(SRb:umQH-7oi0SIc2O\W4F_
WHnU0:=F&8k75T8\<.P65*1fY!]?&c:m6:_<GVu)''`^pnP^biTb1=Y!Di"B^(@kT]1LM@&aZB'1E^>sKEX<_:gD^^do8O&_T:_n_;fol7sFPb2Qo.G@
9^CSB4!7*Bdq;].7F!rnu#0`WA.;C?2e%^IF"-FI!'C[V8K$&P3T[f9&ahqea*fUMLP.lF_.QtWJ#@s)(rLj_/SR?1FmO^#q<691Df[V,j6-9j[ZsUq$
G2E+C61tKde1tmk%02+WEQuDZa%CD2q=gdK;24!kq/qp`)F.+;1(3-MpaA?^0VbjesiYI_/Wp'!'t513f5IJ)IlN\%U(GS^X.Nh8bMHe9rO`">`@2bpL
01<1o^knPNMMC"!To,s],Ie+rFFQdBl`ERM;Hn0Jf_SSufs]8iUu8O#=Q2Kjn#h1BX5%*388jB@VJiK"npP^\_E3lX-cSi2P9EFn^4S\r<%H:bMVfeJ6
BYU=F9Hg.ir+9-q#6-TA_6NCt'XO8/U<)'ng>3C1heu8bu"@qEKN'J;_`d\4&ctFeih4H!I_)f)Z&J.ig?"X\/Z&4hC>En]u7QR`n>'Y>TIpDl<2+Q&j
&^t@@Eca7"%arK[gHKkMlk+hqcL'M5(,KKf@@[.Ar[_5r5#0]Gg<m>hf7"+Y1jN;km'Cu#R?4loVb)*R,hOgi<%[&.446e;!5H`qF)i>-6XGjr0X=ZXK
S@<ICO7R$GdCVqF.^8nTB&fGe1HnR?t6pKE!IMWdRSh"WF,pP&&J:^5^%J[YGb`dBE&elf7Ka3KL0Nu3Pbp>*.f0``*rR$KTn.F5%@_aA!!'?Pbb@<@e
V_R[7josbKQq6hb24*n=!+CW9EA'>N!k88m-q!p+aSfs._8;nV"`r#7nB^n??pY@TC)Gaf/]b,),>8l?l\DQQ@#U`h,QS3Eefs%d;3Vm>_-A7Ykbr@X0
9`Wsf62A*d9,Z!9#QdF6^Ch'S]rDS@Q&fW;ucX/8^G1r4?*^qe3b5/G(VJH@PhPkRaNIS)c^Q_;$NoCXZQDs9p8EpQBZZ5^;L4Du&ZFj_J7s#G<<r=[\
BR/?Ci5Y'Z7,5Rp&/FfUNM,%W5B1>?.=H>"'cQl(Cgpa-Ee*Fhdk,UEK"'YIP@lM)G:1D7]'f(NADoEEU$YqQF"ubl%-Vj=#m,#="rKBY`<PAL1.8OM5
HPYQSO\&jsr#PYYA]EoRpMS'7@pi@>*et'ub?%6jkqr2LrL<I>X@3HQ8Pb'Y'V%T^XU7!s<.9#IO.+KU6@TnL)`8T+1@X$=c`e%H],,MQT@Vk[.:mFqO
Q)5^YBlY)d>NAD>]II"]O)SQiC@`2q0^4@<]^l0^>?$9Nu(>q^],=":9RpOL68(;["XJD.dlBLs*hB%qt#W'YHR1FU80a1@/44i-Y:@g3/9h9Di)R.R6
rD681*h_m*u^B]3mo)epVGIJRtYQI"/Hf`c$24^7A).jVW_V)'mN[BOj/tL/1d$VIm%'&7^f<L8NQL?Osd5"?;%P]V@b=YFMaM#7I?6_SVbrQ$pc@#qi
%UK$UK^._j^GPD`p@+i6R[.)ArqZ/)\aE^1g#puT%ElrHDLes#.D%r!d%qM-IHE*=K@8e8)V\E-qCJi0OKNUR>a6sX_!4mZ1aZiOOMSJL]ms6&t!_^37
[44(Gg./=;m(hDt'hUi<sJU+dT+1_-5Lt,e=Dp>U4?8f-\mB^V_H'S)^o+=.UjR0T9Y7VA)3LVGDC=qJM\0P!kR>DnJmbdhd$,"XQV:F$HV49+,b8Qo9
P_#X_7jt@e[N\XXZ*UOUb=Qdo?IP]?cFqL?Z.i+(^dAJXcEpZ>&j*UbhfJu=l@@Tt4Z08K@e-o[690_;?uQZ:#/nK+T1VDRXWk4P`t!_Om60rq,"44-j
\Vq_p%&c%IqS.Y246<@*g;;85@GM8>Z_]-fGb+CqM6fgcN2EalCKJJ3OF^,AP.Q/iN\+V_2$s5eS`KsEAmp8@`W`<prlr<8%Hh"@(P*>Z*+ULcs0gkJ\
>hmQ>CZPfP"LuGEMLkAJt:L,p9,%P"C(pMa_k$kXp^.JmgF^#AY,V)>a>6(g@WjhS6bA+]OipGoAJ^?jX]<Q#H*:'ar0DXmr'kqBTS1/iS(E+NN3q*?>
fKMo%6mfhK-^okmPsq5\c@W;Kk9'^O]ig=e8t:s9J$#a!XhIk:Xn_"L9m2/11B02)^"_E!jhNu_`d7:r?n:#3MtHRE<[^cT<(:NJEE/91Hh:YU(#)EnJ
<b)f^u1SjGALA\2t7;WX'cm#.,L@sfhip,&[SojPYgFbG;o>KJF"\3'j3-">Vm"G-rjmXW(>qhmj,+`i9/^L->#-L9Y*,\D/05s^E"IoLapp@&e=S1fB
'&"&i5K#qiit2P>K^3s.ekda!kT>3G>?'QT/Du@RkF0E,8*aqti4V;NbCRLl]/42iP=e1^N6HE@ga;RdM?gUr/pbV'.4?/SPa'UAmgk(0@XL,1@8ecS@
lN@.Vkg*URU=(M_\_]_$smD&J;VV#<EeZFdO%6`?37&YO`qU.AbA'b"2AuZPJtLP++BfH*`YC^IpRUl/<h\L#u$G1?I=In:SQd7P9?&%=%1>aGU$+5HN
+E+qqXheGIG$lYFm4GMC5YqAD4\.Z[D,ceI;&Ib(oS[N;r)lK)12A57R+0M7[_`"Ib\:U'Cf616T8WlJ^$q$37^9S*,R9iA$Ctcr/.Q'/K+?n7.n9R%B
\*B>VjQ$d/IdP)1V5#ucOIMmG+snNmCOHdZW]o[olQ,,Tn(^:t\$m2&WRElJUVDo.kbE*Z@1P7"=&Q[;a?6DqK[f=HFN$SoNH,sm?7Bb!#\;IY.++DVW
7rR5?mV.XR*fnBeB5j``#8Rq#DnJ;H7[35PpX$_cW.u-L!#BX5u'(AAA5]W-o1o6C9o0XJS93TfA:3aui1TG,e@ZC#:P2`TPU_.eFB7OEsVXk>X\%@)b
^!ZDDCA00`#&R2Xg*(i=?6`hY%At;3Fp@_i$=^9>8Fj?Pm%cH@+a[?_SJ@E6Vs-i:s%pK<3++!d#/(8ch)'8ZNN`Z+6fk#6(W7!QA1\Qoq"m!d@2_n64
9?aPXU<[uc+ba"'c'[Ae<MN`X:fF!Zknc%15LW5,_h\:OUmD`\+PSP+o3_J$1KjCm#L=qNu&T/(]LsDZT(J7af<iA?O;KX&D5=0d#&k7+=jfbdm]5U\B
EF[rISA1]-hEUb9!mC%1(A"QcB@TH-(;fn=@"TiPn)B]QF(+.)YNo7`GGqr+P,`:k;1K*o6PZ+5[I#R/a['0[Q2/9JFp=mpd0XKsGHCb?<>U-1qEq'E<
4/TgE"3!A%r5KL,,tEqG6,Ynd6f@`\P32hNh=)sYb++,?&qOqFHUj9T',e=sWWag%0V);'Du3DtIJ-WE=(Q["=;EAeg!1Qi=HX]3B/o`^hAGqi\+aMbF
QWkY3)=Duo]_VMp5?RFDtEE<i!;99(l5r+SR<[/1G_GfY?WsjdK$?8AiHY(Hd3kqM][A@a/^Jj5P8-.7NnPOEr9mi)Mk!j7X9AptH[fN2$_0l:R;M=%R
2'X4<PE&B@Tn_NH\B!E]i-!I\Xt"O40=Cfh/HrcA6g.R@8uq7=&_I5a5jPWsoKFr<+Qmb;L?`OT"'D8^NjmMqG"_8U$Jn\)6;m#dQJLWN_e.I\,9QKp4
/"h<CC+!\J(PI1RIEj5_FJ"A\]Ud?1u@KQkMbl5G&VVg#hYNrgWWNfKY:fp`#jh)D"TFg`ZV^0j@dI9g+OKXq,[g@3IR&W%NBO5*kZ<mluXGqU+//6:X
*gV`k+Xg$#LhlMhXfmm=0:^lAYYrZ1u6HU;0guH.O)!r$5-$-/[[b,/@`ll[SbDbKf,JVNN!_(?5l/>9*]*laZ=iaAcj%q?cB<C(G&;8i%7p_:mACPk(
L0k&m5^2PcFDTV3TUGPD4+$VKr5K@hg@i#K\iLADK<8k$0m\P@0!"5;@5(I:uI+:/.*C_3G<^=Sr;($QTdNbt0K:*-gO]0ZI#$0&$*:4WupiO9'(*TB@
%I`0lA&:"gI(rg=[>u^GZXCf=J:l?@U*Ef"-9_LnLeDY@WYLJX;Fg]j1B*-ZC]r2V@6%BEg`7tn/c#^/\UX[&L3!JhGJ'F@jfc/Zc_$5uu==5^g.\N^'
c6aJqWJC\"+WtV\0>^>Lb6Z/Jrl2gZ'm$aIPFO?!RK!i5Dc>[kUd2p8CIuh#4%WdPI)hndcX0KEHo9D,3W2!NPeOogm>eA/;uqiD/!UD![gBJ;%Y?#f(
N8,hf&WGlZtJ=j?4_Tj:n!2i*3\Yr4&Uq1M5jF1oDC+$2m8"uL;cT1Ag8JLUQNQsoeZ>2pu:%2JiTjX+J>-Jn9<73"NaYGbQ@,ST0JfG+Q\),KWho@OK
s5kq6R=-&+ZUGYLX-*lT#X2AkVWFC?!$)nTr.ur6A#5<or:o6DDJ+\`YSmDX;,L!9RG)a`2$i*r%,k:mX42P4f1$-</<QVlt;d%!L^NFPbmp(R\+3%4Z
fM2_:g@i4>;5-Ih&+7:W>@<L$-rj\J(2k(uZ!2-FFV[RZ1#d\28MR%sS>'4QX2f_n-I]b(udnNG(\biHeZW\n9@K&#SOWB9;D[,s@t\05H69_-qP2P4q
rmg_!W,M5hYPuogEW!Iq&4e?=7j5FFD(:0nJi'f%ODOLp-4FNri.uI2JN8_&n]sQn+gkE"[J\jsW[DaH9S=T<7BC-<oG(ou.D0$IN+?O;qW2srEPOE`D
7)m@%G3TH_Ps"Lnd'0m=BheO>d'XG:4u[&,s44=-504b]<t1Y\BKHpXT!p*q4u;Ds`GJnnAL`dW*itIM@D:H2'"c3phs[M_GfW?7FYTrYnTA"@+5eh<X
/..-mr6CIUFO'6anE?]rsX7"$4Rf$W+/B<0_SNAOC24BqeI<"i^t#kef0s'SK&"+kc[bmac0[\YTVu8@<CFTlWPK-n7TsjR94UupYX5eEE1%CJGm)qT5
ed([+AP2>'_so3F5UqSH8Z9a%+gu@S0Ft"^HWp(_+.q8M&Y2V*WZ$4pDo\&M,:u,`iqK&Q!;A2o:\s3nQLA[Lk?6ZVT,FVDIa`V."8_cPCTIO_2g3d2q
"E[O:DXAkN.3[A$He"PmS.A#=8-P^)_2`onio:e!'2]kDZ#;!43qcM<G'9?o)9`BA"8c$D@_X"S$6)fu!HqA"\#[p^0M&GVoTqc0Mo+SNj`M?=Ts7A,A
RCJ/lr3].]MURVbu9.1We8]c&J,E<\W'10<OX5+9$3,@[uH(6E"?V%sDNP10gH97eQgKh!=%9bgMT%%3gG1>]^.97m+9@YL4^W%2q$u87t@Y\,e5'Z0l
*8AXs$WG4i_R*EGN/p2nhL>EpHeq5[T_45seP[D\,WQ[3-T)0r-fL[M)dcOO3gMDiVfZ[eS**b`"I<dIM\%E/cVVo`L+foT.NcEmi0-F7c?aVk&qla(m
Rn\j#_I;\5S7!1NA"O]Z3%R/)CmZ"18_pcd>`C%QsduLcGI)mZ\2S]%[<D!Z&:s-Yaq5l0A\*IT`aM5M+:@N,97_Zh',aU%'j$$b:fK+9A[1bCG_d!8c
oV^*jo-)m?!70g^1TNeLl3Y^hG^?^Em)(%Lb50>#LU0c%.+-2LsgAF]TrIE!Tc$n>&1J'J19M7hrAdZh6@3+/"J5RNhg%?L.h5#R'aSj4aSE9<()Z@8A
eHShZ".,1rGFW)d6Go22Ak<&Wu)'q:iAR3-ac2\jnt(>C5(A?1P8'#:7g_KeY"34[5h6,#knOr79FM#r$iierNpi5,N9=e4'rXguLb]XtDK!7QuPYC$`
'p5:sV`S&I`5lHAjkp'_a\/_[iHD?j*5,8[KB1nkfYdUG?jirL&]+%5_[dPKW\hL%cV3);V2-Zh!cNHXYc&(M$jiX:Jeq%`]hePd_HUq(oqqi1Z`SpL]
\9^4C7ZXLgU]H,O1,`_elO0liI'UTpXo@Ie<`97'1/iW<?6K4#.:;"=h=/T%eN?X(7pX4G>7NtCAe=UHX4>s4X+*6F.+;E3TItS8O&0kEB;/946mA'US
Tcb`!E:T*3N#uW(&#4=io3X82kNI0#Wj5KM3l;=l.a^KRP,B%;ns.l1B9?l'bs/>oC0:T0%=Q^P#7h+[Cp9a*2jJ3'ak#+8<c40^:=p+DrelZK0@h&on
BT3caX.mHnYS4JXZKs6_,K;PU.]O3AsrLU7NBVh:i[3%b_&E!L]nogporM74Ws2qi`1(TuIF-UfR%,q8kn`_.E(M^7?VRVAS2F+j=ZXglJ_jM\ji/4k#
PH[^TL`>cUKd`:KS^M7lrk;fg],SsV%E0HD:G9tlPco2i>'QQY!QHq__HoC**HbjMb(@_J/1`.K/>1OKp-qcWTE)OuL!*c("sF<K"aq.k>n,3,q;5*rH
=YZ0eS'Jg_lmGWrMek>*A37=LN)>XG5='"@/<3[)9l3=3&A0Ct)'&eb\-#a_^.iu9;<;n@uG4ed\;t]'%B1P&a3Q[H"^KR*TK4i#$KF.C>QA9R]LkOhq
4`2C"`66`Vs*4ZIQi>(!N.($`ZQ^!U4X'Tt#n(^*bJJC5KGj38X:bjcO>V_.laQR8m91r#@mc!ZZ,O[RTPI3?71;TJXXnL8<G[QWD,gY?b5QDB>Zuo*g
KTBBe`=UNfrS"$kd<o$9gi.-0&nhD1@8QjjiFtbJ4E8(HVgbf#!.*%nQsr&Xd->@G0>PpA\=EpV$ckclK)7iKmmcj$#'cVYf4VW(;&17+Y/l&Q=NL-0F
jpS<39J*K!n*Z;Uab/X\_SGs1;9/CcZC]^>UIfoshUQX+AN\as7f\943D]>`FDdX`K-Jd0F7(Ht2DjU3GN>$?!/tc42]D\gj7l<;g=X[%&?\ID6]/AZ_
7XdqEB>]6c"GXV9]MRH\p,jBeb_Ikc866VS/j%C,a#9\!\;od5McS>@0p,m>>P2RTm+eOH7BjUj>M[T\rUr"c5^ptPTOrI^inDOZ5^?A)SMM6c<do;CS
8#`QZ#V'u1dipY!A:8Z62T5V9,5``Z>cbs_'!-2$W(SCUjB.9^E?jmTo28fI%O=0SZO\17/<O&4%;OfG-cJe1abjHfdP`9"Jhp%;<AntW;j.Q&>X65m_
f*Mp)*FX)6ago\?(P<lh*pg-'Kb"Wc)JMPDW/g4!Ff7,!P[e>bBN2gMXrAP[Xgp5!Go>4A&-t3oWmAWpF-i7JGi-UT813=)kQ6pE6t]sl=#nNW%tb@/8
WJ)?&u#74Vbab%Y\VI>@`4`UF<^)jh>hV;Tppm6O"VC6RON1r&_B&5."l70FZ]*3?FFLdku9,[(8jk!fDk_#=b_9tCG'ssc%7I'n0>31a?qP3CE;D%*^
W:-cb.I;=qhlkb<8R7)W_,hXf!'CckKW@K)abt,e`<ZF*Q4)`Tmj[<&%GSW]!IT"cOQ@Z(9%\O4-fhc)A*4S3K4?A]ioVbKX%BnJ`Wt4qN#+'&3RQOBH
L(0>5]R/'5[AI'LIN$XC_lTp/24DRL0^gS[BVH"en),:l;$C;WK4F?P!S[IoJ!qi*ftb,(<D28C8Lb+F^uNEFNXA8M?>p#bfKK&TGQi/;Rhh3Ng5Ba@N
'erkE+FoD(2pBn'cM_+HG)]ta0g\L@&VVl%Z:E'`J[iN2:5)Vgt,cd[SEEDDi^mM2j,bbhG(?5I?m]`MHhOB7A9s9]6q#JfbKVS-tN"d`A`MMcI7PDrR
!!0HY!NjiR]:N`,Z,C;P!WW3#!!HG.'''
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.59'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-11-06'

# smartmontools installs into sbin, which non-root PATHs often omit (e.g. Debian),
# yet `--sudo` exists exactly for non-root users who want SMART.
SMARTCTL_FALLBACK_DIRS = ["/usr/sbin", "/sbin", "/usr/local/sbin", "/opt/homebrew/sbin"]

def find_smartctl(fallback_dirs=SMARTCTL_FALLBACK_DIRS):
	return shutil.which("smartctl") or shutil.which("smartctl", path=os.pathsep.join(fallback_dirs))

SMARTCTL_PATH = find_smartctl()
DISKUTIL_PATH = shutil.which("diskutil")
IS_DARWIN = (sys.platform == "darwin")
MOUNTINFO_PATH = '/proc/self/mountinfo'
_DEBUG_MODE = False
LSBLK_PAIR_RE = re.compile(r'(\w+)="([^"]*)"')
# Output columns that come (at least partly) from the lsblk call on Linux.
LSBLK_FIELDS = {'SIZE', 'FSTYPE', 'UUID', 'LABEL', 'MODEL', 'SERIAL'}
# The columns the note below names (SIZE and LABEL have their own sysfs and /dev/disk sources).
LSBLK_NOTE_FIELDS = {'FSTYPE', 'UUID', 'MODEL', 'SERIAL'}
LSBLK_MISSING_NOTE = "lsblk not found (it comes with util-linux): FSTYPE, UUID, MODEL and SERIAL come from sysfs and /dev/disk instead and may be incomplete."
_OCTAL_ESCAPE_RE = re.compile(r'\\([0-7]{3})')
_HEX_ESCAPE_RE = re.compile(rb'\\x([0-9a-fA-F]{2})')

def debug_exc(context, exc):
	if _DEBUG_MODE:
		print(f"DEBUG [{context}]: {exc}", file=sys.stderr)
		traceback.print_exc()

def compile_filter_pattern(filter_patterns):
	"""Compile CLI filter patterns into one regex.

	>>> p = compile_filter_pattern(['sda', 'nvme'])
	>>> bool(p.search('sda1'))
	True
	>>> bool(p.search('hd0'))
	False
	"""
	try:
		return re.compile('|'.join(filter_patterns))
	except re.error as e:
		print(f"Invalid filter pattern: {e}", file=sys.stderr)
		sys.exit(1)

def _decode_proc_path(path):
	r"""Decode the octal escapes the kernel uses in /proc mount paths
	(space, tab, newline and backslash).

	>>> _decode_proc_path('/mnt\\040disk')
	'/mnt disk'
	>>> _decode_proc_path('/mnt/disk')
	'/mnt/disk'
	"""
	if '\\' not in path:
		return path
	return _OCTAL_ESCAPE_RE.sub(lambda m: chr(int(m.group(1), 8)), path)

def _decode_hex_escapes(text):
	r"""Decode \xNN byte escapes used by lsblk -P and udev symlink names.

	Escaped bytes are reassembled before UTF-8 decoding, so multi-byte
	characters escaped one byte at a time come back intact.

	>>> _decode_hex_escapes('my\\x20label')
	'my label'
	>>> _decode_hex_escapes('plain')
	'plain'
	"""
	if '\\x' not in text:
		return text
	raw = _HEX_ESCAPE_RE.sub(lambda m: bytes([int(m.group(1), 16)]), text.encode('utf-8'))
	return raw.decode('utf-8', errors='replace')

def parse_lsblk_pairs_line(line):
	"""Parse one lsblk -P output line into a {column: value} dict.

	>>> fields = parse_lsblk_pairs_line('NAME="/dev/sda" SIZE="107374182400" FSTYPE="ext4" UUID="abc-123" LABEL="boot"')
	>>> fields['NAME'], fields['SIZE'], fields['FSTYPE'], fields['UUID'], fields['LABEL']
	('/dev/sda', '107374182400', 'ext4', 'abc-123', 'boot')
	"""
	return {key: _decode_hex_escapes(value) for key, value in LSBLK_PAIR_RE.findall(line)}

def populate_lsblk_dicts(stdout, output_fields_set, uuid_dict, fstype_dict, label_dict, size_dict,
						model_dict=None, serial_dict=None):
	"""Populate device metadata dicts from lsblk -P stdout lines.

	MODEL/SERIAL come from udev via lsblk and are only set on whole disks.

	>>> u, f, l, s = {}, {}, {}, {}
	>>> populate_lsblk_dicts(
	...     ['NAME="/dev/sda" SIZE="100" FSTYPE="ext4" UUID="u1" LABEL="l1"'],
	...     {'SIZE', 'FSTYPE', 'UUID', 'LABEL'}, u, f, l, s)
	>>> s['/dev/sda'], f['/dev/sda'], u['/dev/sda'], l['/dev/sda']
	(100, 'ext4', 'u1', 'l1')
	"""
	for line in stdout:
		line = line.strip()
		if not line:
			continue
		try:
			fields = parse_lsblk_pairs_line(line)
			lsblk_name = fields.get('NAME', '')
			lsblk_size = fields.get('SIZE', '')
			lsblk_fstype = fields.get('FSTYPE', '')
			lsblk_uuid = fields.get('UUID', '')
			lsblk_label = fields.get('LABEL', '')
			if lsblk_name.startswith(os.path.sep):
				lsblk_name = os.path.realpath(lsblk_name)
			if 'UUID' in output_fields_set and lsblk_uuid:
				uuid_dict[lsblk_name] = lsblk_uuid
			if 'FSTYPE' in output_fields_set and lsblk_fstype:
				fstype_dict[lsblk_name] = lsblk_fstype
			if 'LABEL' in output_fields_set and lsblk_label:
				label_dict[lsblk_name] = lsblk_label
			if 'MODEL' in output_fields_set and model_dict is not None and fields.get('MODEL'):
				model_dict[lsblk_name] = " ".join(fields['MODEL'].split())
			if 'SERIAL' in output_fields_set and serial_dict is not None and fields.get('SERIAL'):
				serial_dict[lsblk_name] = " ".join(fields['SERIAL'].split())
			if 'SIZE' in output_fields_set:
				size_dict[lsblk_name] = int(lsblk_size)
		except Exception as e:
			debug_exc('lsblk line', e)

def read_text(path):
	try:
		with open(path, "r", encoding="utf-8", errors="ignore") as f:
			return f.read().strip()
	except Exception:
		return None

def read_int(path):
	s = read_text(path)
	if s is None:
		return 0
	try:
		return int(s)
	except Exception:
		return 0

def build_symlink_dict(dir_path):
	"""
	Build map: devname -> token (uuid or label string) using symlinks under
	/dev/disk/by-uuid or /dev/disk/by-label.
	"""
	mapping = {}
	if not os.path.isdir(dir_path):
		return mapping
	try:
		for entry in os.listdir(dir_path):
			p = os.path.join(dir_path, entry)
			try:
				if os.path.islink(p):
					tgt = os.path.realpath(p)
					mapping.setdefault(tgt, _decode_hex_escapes(entry))
			except Exception:
				continue
	except Exception:
		pass
	return mapping

def parse_bytes_from_diskutil_size(value):
	"""Extract byte size from diskutil size strings.

	>>> parse_bytes_from_diskutil_size('100.0 GB (107374182400 Bytes)')
	107374182400
	>>> parse_bytes_from_diskutil_size('')
	0
	>>> parse_bytes_from_diskutil_size('no bytes here')
	0
	"""
	if not value:
		return 0
	match = re.search(r"\((\d+)\s+Bytes\)", value)
	if match:
		try:
			return int(match.group(1))
		except Exception:
			return 0
	return 0

def get_macos_diskutil_info(timeout=4):
	"""
	Build map: /dev/diskXsY -> info from `diskutil info -all`.
	Only used on macOS.
	"""
	if not IS_DARWIN or not DISKUTIL_PATH:
		return {}
	info_map = {}
	current = {}
	rtn = multiCMD.run_command(f"{DISKUTIL_PATH} info -all", timeout=timeout, quiet=True)
	for raw_line in rtn + [""]:
		line = raw_line.rstrip("\n")
		if not line.strip():
			devnode = current.get("Device Node", "").strip()
			if devnode:
				size_bytes = parse_bytes_from_diskutil_size(current.get("Disk Size", ""))
				if size_bytes == 0:
					size_bytes = parse_bytes_from_diskutil_size(current.get("Volume Total Space", ""))
				model = (current.get("Device / Media Name") or current.get("Media Name") or "").strip()
				serial = (current.get("Serial Number") or "").strip()
				fstype = (current.get("File System Personality") or "").strip()
				label = (current.get("Volume Name") or "").strip()
				uuid = (
					current.get("Volume UUID")
					or current.get("Disk / Partition UUID")
					or current.get("APFS Volume Disk (Role)")
					or ""
				).strip()
				solid_state = (current.get("Solid State") or "").strip().lower()
				if solid_state == "yes":
					discard = "Yes"
				elif solid_state == "no":
					discard = "No"
				else:
					discard = "N/A"
				info_map[devnode] = {
					"SIZE_BYTES": size_bytes,
					"FSTYPE": fstype,
					"UUID": uuid,
					"LABEL": label,
					"MODEL": model,
					"SERIAL": serial,
					"DISCARD": discard,
				}
			current = {}
			continue
		if ":" in line:
			key, value = line.split(":", 1)
			current[key.strip()] = value.strip()
	return info_map

# mountpoint -> daemon thread still blocked in os.statvfs from an earlier call.
_HUNG_STATVFS = {}
# Floor on the statvfs wait, so healthy mounts still get answered after a stuck
# smartctl has used up the refresh deadline.
STATVFS_MIN_WAIT = 0.5

def _statvfs_with_timeout(mountpoint, timeout):
	"""os.statvfs that gives up after `timeout` seconds (dead NFS/CIFS server).

	Returns None on timeout. The blocked thread can't be cancelled, so it is
	remembered and later calls for that mountpoint return None right away
	instead of piling up another stuck thread every watch refresh.
	"""
	hung = _HUNG_STATVFS.get(mountpoint)
	if hung is not None:
		if hung.is_alive():
			return None
		del _HUNG_STATVFS[mountpoint]
	result = {}
	def run():
		try:
			result['st'] = os.statvfs(mountpoint)
		except Exception as e:
			result['error'] = e
	thread = threading.Thread(target=run, daemon=True)
	thread.start()
	thread.join(timeout)
	if thread.is_alive():
		_HUNG_STATVFS[mountpoint] = thread
		return None
	if 'error' in result:
		raise result['error']
	return result['st']

def get_statvfs_use_size(mountpoint, timeout=None):
	"""Return (total_bytes, used_bytes, avail_bytes) like GNU df, or None if
	statvfs did not answer within `timeout` seconds (None = wait forever).

	used = (f_blocks - f_bfree) * frsize  — actual allocated blocks, not counting
	root-reserved space as used. avail = f_bavail * frsize (space non-root can use).
	FSUSE% should be used / (used + avail), matching df Use%.
	"""
	try:
		if timeout is None:
			st = os.statvfs(mountpoint)
		else:
			st = _statvfs_with_timeout(mountpoint, timeout)
			if st is None:
				return None
		block_size = st.f_frsize if st.f_frsize > 0 else st.f_bsize
		total = st.f_blocks * block_size
		avail = st.f_bavail * block_size
		used = (st.f_blocks - st.f_bfree) * block_size
		return total, used, avail
	except Exception:
		return 0, 0, 0

def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	return 'Yes' if dmbytes > 0 else 'No'

def get_real_sysfs_device_path(sysfs_block_path):
	"""
	Return the sysfs 'device' directory for this block node (resolves partition
	to its parent device as well).
	"""
	dev_link = os.path.join(sysfs_block_path, "device")
	try:
		return os.path.realpath(dev_link)
	except Exception:
		return dev_link

def read_model_and_serial(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return '', ''
	device_path = get_real_sysfs_device_path(sysfs_block_path)
	model = read_text(os.path.join(device_path, "model"))
	serial = read_text(os.path.join(device_path, "serial"))
	if serial is None:
		serial = read_text(os.path.join(device_path, "wwid"))
	if model:
		model = " ".join(model.split())
	else:
		model = ''
	if serial:
		serial = " ".join(serial.split())
	else:
		serial = ''
	return model, serial

def read_size(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 0
	sectors = read_int(os.path.join(sysfs_block_path, "size"))
	return sectors * 512 # linux kernel uses 512 byte sectors

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])

def parse_mountinfo_line(line):
	"""Parse one /proc/self/mountinfo line into (device, MountEntry).

	>>> dev, ent = parse_mountinfo_line('998 997 0:34 /root / rw,relatime - btrfs /dev/sda3 rw')
	>>> dev, ent.MOUNTPOINT, ent.FSTYPE, ent.OPTIONS[:2]
	('/dev/sda3', '/', 'btrfs', ['rw', 'relatime'])
	>>> parse_mountinfo_line('too short') is None
	True
	"""
	parts = line.strip().split()
	if len(parts) < 10:
		return None
	try:
		dash_idx = parts.index('-')
	except ValueError:
		return None
	if dash_idx < 6 or dash_idx + 2 >= len(parts):
		return None
	mount_point = _decode_proc_path(parts[4])
	mount_options_str = parts[5]
	fstype = parts[dash_idx + 1]
	device_name = _decode_proc_path(parts[dash_idx + 2])
	if device_name.startswith(os.path.sep):
		device_name = os.path.realpath(device_name)
	options = [x.strip() for x in mount_options_str.split(',') if x.strip()]
	return device_name, MountEntry(mount_point, fstype, options)

def parse_darwin_mount_line(line):
	"""Parse one macOS mount(8) output line into (device, MountEntry).

	>>> dev, ent = parse_darwin_mount_line('/dev/disk3s1 on / (apfs, local, journaled)')
	>>> ent.MOUNTPOINT, ent.FSTYPE, ent.OPTIONS[1]
	('/', 'apfs', 'local')
	>>> parse_darwin_mount_line('not a mount line') is None
	True
	"""
	match = re.match(r"^(\S+)\s+on\s+(.+?)\s+\((.*)\)$", line)
	if not match:
		return None
	device_name = match.group(1)
	if device_name.startswith(os.path.sep):
		device_name = os.path.realpath(device_name)
	mount_point = match.group(2)
	options = [x.strip() for x in match.group(3).split(",") if x.strip()]
	fstype = options[0] if options else ""
	return device_name, MountEntry(mount_point, fstype, options)

def parseMount():
	mount_table = defaultdict(list)
	def add(parsed):
		# Skip autofs triggers: stat-ing them mounts the target (df skips them
		# too); the real filesystem shows up as its own entry once mounted.
		if parsed and parsed[1].FSTYPE != 'autofs':
			device_name, entry = parsed
			mount_table[device_name].append(entry)
	if IS_DARWIN:
		rtn = multiCMD.run_command('mount', timeout=1, quiet=True)
		for line in rtn:
			add(parse_darwin_mount_line(line))
		return mount_table
	try:
		with open(MOUNTINFO_PATH, 'r', encoding='utf-8', errors='ignore') as f:
			for line in f:
				add(parse_mountinfo_line(line))
	except Exception as e:
		debug_exc('parseMount', e)
	return mount_table

def get_blocks():
	if IS_DARWIN:
		# On macOS, enumerate /dev/diskN, slices (diskNsM) and APFS snapshot
		# nodes (diskNsMsK — the sealed system volume mounted at / on 11+).
		block_devices = []
		try:
			for entry in os.listdir("/dev"):
				if re.match(r"^disk\d+(s\d+)*$", entry):
					block_devices.append(f"/dev/{entry}")
		except Exception:
			pass
		return sorted(block_devices)
	# Linux: get entries in /sys/class/block
	block_devices = []
	try:
		for entry in os.listdir("/sys/class/block"):
			if os.path.isdir(os.path.join("/sys/class/block", entry)):
				block_devices.append(f'/dev/{entry}')
	except Exception as e:
		debug_exc('get_blocks linux', e)
	return block_devices

def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False

def get_mapper_path(device_name):
	"""Map /dev/dm-N to its /dev/mapper/<name> alias (e.g. pve-root); other
	devices are returned unchanged."""
	if IS_DARWIN or not os.path.basename(device_name).startswith('dm-'):
		return device_name
	dm_name = read_text(os.path.join('/sys/class/block', os.path.basename(device_name), 'dm', 'name'))
	return '/dev/mapper/' + dm_name if dm_name else device_name

def display_device_name(device_path, full):
	"""Shown NAME: the full path with -R/--full, else without the /dev(/mapper)/ prefix.

	>>> display_device_name('/dev/mapper/pve-root', False)
	'pve-root'
	>>> display_device_name('/dev/sda1', False)
	'sda1'
	>>> display_device_name('/dev/sda1', True)
	'/dev/sda1'
	"""
	if full:
		return device_path
	for prefix in ('/dev/mapper/', '/dev/'):
		if device_path.startswith(prefix):
			return device_path[len(prefix):]
	return device_path

def has_sysfs_device(disk):
	"""True if the disk is backed by real hardware (sysfs 'device' link).

	loop, dm, md, zram and nbd devices have no such link and no SMART data.
	"""
	return os.path.exists(os.path.join('/sys/class/block', os.path.basename(disk), 'device'))

def has_smart(parent_name):
	"""True if SMART should be readable for this disk: a hardware-backed disk
	on Linux, any disk on macOS. A blank SMART value on such a disk would mean
	"not checked", so it is shown as NO SMARTCTL / UNKNOWN instead."""
	return bool(parent_name) and (IS_DARWIN or has_sysfs_device(parent_name))

def is_squashfs_loop(device_name, fstype):
	"""True for a squashfs image on a loop device (snaps, AppImages): read-only
	and always 100% full, so it is hidden unless --show_squashfs.

	>>> is_squashfs_loop('/dev/loop0', 'squashfs')
	True
	>>> is_squashfs_loop('/dev/loop1', 'ext4'), is_squashfs_loop('/dev/sdb1', 'squashfs')
	(False, False)
	"""
	return fstype == 'squashfs' and os.path.basename(device_name).startswith('loop')

def get_partition_parent_name(name):
	if not name:
		return None
	name = os.path.basename(name)
	if IS_DARWIN:
		match = re.match(r"^(disk\d+)(s\d+)+$", name)
		if match:
			parent = os.path.join("/dev", match.group(1))
			return parent if is_block_device(parent) else None
		dev = os.path.join("/dev", name)
		return dev if is_block_device(dev) else None
	sysfs_block_path = os.path.realpath(os.path.join('/sys/class/block', name))
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return None
	part_file = os.path.join(sysfs_block_path, "partition")
	if not os.path.exists(part_file):
		return os.path.join('/dev', name) if is_block_device(os.path.join('/dev', name)) else None
	parent = os.path.basename(os.path.dirname(sysfs_block_path))
	return os.path.join('/dev', parent) if parent and parent != name else None

# Kernel block layer always reports /sys/block/*/stat sector counts in 512-byte
# units, regardless of queue/hw_sector_size or logical_block_size.
STAT_SECTOR_BYTES = 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
	"""Yield (read_Bps, write_Bps) samples for a block device.

	The first sample is a lifetime busy-time average: total bytes transferred
	divided by time spent doing I/O since boot (from the stat time fields).
	That gives an immediate non-zero estimate without waiting for a poll interval.

	Later samples are interval rates: delta bytes / wall-clock elapsed since the
	previous sample (used by watch mode after the first refresh).
	"""
	if IS_DARWIN:
		# Per-device throughput is Linux /sys stat based; return zeros on macOS.
		while True:
			yield 0, 0
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield 0, 0
	rx_path = os.path.join(sysfs_block_path, "stat")
	start_time = time.monotonic()
	sector_size = STAT_SECTOR_BYTES
	previous_bytes_read = 0
	previous_bytes_written = 0
	try:
		with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
			fields = f.read().strip().split()
		if len(fields) < 8:
			yield 0, 0
		else:
			sectors_read = int(fields[2])
			read_time = int(fields[3]) / 1000.0
			sectors_written = int(fields[6])
			write_time = int(fields[7]) / 1000.0
			read_throughput = (sectors_read * sector_size) / read_time if read_time > 0 else 0
			write_throughput = (sectors_written * sector_size) / write_time if write_time > 0 else 0
			previous_bytes_read = sectors_read * sector_size
			previous_bytes_written = sectors_written * sector_size
			yield int(read_throughput), int(write_throughput)
	except Exception as e:
		debug_exc('throughput initial', e)
		yield 0, 0
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				fields = f.read().strip().split()
			if len(fields) < 7:
				yield 0, 0
				continue
			# fields: https://www.kernel.org/doc/html/latest/block/stat.html
			# 0 - reads completed successfully
			# 1 - reads merged
			# 2 - sectors read
			# 3 - time spent reading (ms)
			# 4 - writes completed
			# 5 - writes merged
			# 6 - sectors written
			# 7 - time spent writing (ms)
			# 8 - I/Os currently in progress
			# 9 - time spent doing I/Os (ms)
			# 10 - weighted time spent doing I/Os (ms)
			sectors_read = int(fields[2])
			sectors_written = int(fields[6])
			bytes_read = sectors_read * sector_size
			bytes_written = sectors_written * sector_size
			end_time = time.monotonic()
			elapsed_time = end_time - start_time
			start_time = end_time
			read_throughput = (bytes_read - previous_bytes_read) / elapsed_time if elapsed_time > 0 else 0
			write_throughput = (bytes_written - previous_bytes_written) / elapsed_time if elapsed_time > 0 else 0
			previous_bytes_read = bytes_read
			previous_bytes_written = bytes_written
			yield int(read_throughput), int(write_throughput)
		except Exception as e:
			debug_exc('throughput poll', e)
			yield 0, 0

def natural_sort_key(text):
	"""Sort key that orders embedded numbers numerically.

	>>> sorted(['sda10', 'sda2', 'sda1'], key=natural_sort_key)
	['sda1', 'sda2', 'sda10']
	"""
	# re.split with a capture group alternates text/number, so positions line up.
	return [int(part) if i % 2 else part for i, part in enumerate(re.split(r'(\d+)', text))]

def _remaining(deadline):
	"""Seconds left until a time.monotonic() deadline (None = no deadline)."""
	if deadline is None:
		return None
	return max(0.0, deadline - time.monotonic())

def _boot_seconds():
	"""Seconds since boot, the clock /proc/<pid>/stat starttime counts from.
	Not /proc/uptime: lxcfs shows a container's own uptime there. 7 is CLOCK_BOOTTIME on Linux (Python 3.6 lacks the name)."""
	return time.clock_gettime(getattr(time, 'CLOCK_BOOTTIME', 7))

def find_stuck_smartctl(older_than, proc='/proc'):
	"""Set of disks (real paths) that already have a smartctl running for more
	than `older_than` seconds, from an earlier refresh, run, cron or other tool.

	On a dying disk smartctl sits in uninterruptible I/O and can't be killed, so
	starting another one only adds to the pile. Linux only: no /proc, empty set.
	Only a smartctl's cmdline is read (and that of a process whose comm is a
	number, see below): reading another process's can block on its memory (swap
	on a dead disk, a wedged mm lock), and stat touches none.
	"""
	stuck = set()
	try:
		pids = [p for p in os.listdir(proc) if p.isdigit()]
		boot = _boot_seconds()
		clk_tck = os.sysconf('SC_CLK_TCK')
	except (AttributeError, OSError, ValueError):
		return stuck
	for pid in pids:
		try:
			stat = read_text(os.path.join(proc, pid, 'stat'))
			# comm (field 2, the executable's basename) may hold spaces and parentheses:
			# it runs to the last ')', and the numbered fields follow it.
			comm = stat[stat.index('(') + 1:stat.rindex(')')]
			# sudo runs a command pinned by digest through its file descriptor (fexecve):
			# before Linux 6.14 its comm is then that number, so argv[0] tells.
			if comm != 'smartctl' and not comm.isdigit():
				continue
			starttime = int(stat.rsplit(')', 1)[1].split()[19])
			if boot - starttime / clk_tck > older_than:
				argv = read_text(os.path.join(proc, pid, 'cmdline')).split('\0')
				if comm.isdigit() and os.path.basename(argv[0]) != 'smartctl':
					continue
				stuck.update(os.path.realpath(a) for a in argv[1:] if a.startswith('/dev/'))
		except (AttributeError, IndexError, OSError, ValueError):
			continue  # gone or unreadable: not ours to report
	return stuck

# What `smartctl -n standby` prints when it skips a spun-down drive (SLEEP,
# STANDBY, or variants like STANDBY_Y) instead of waking it.
SMART_STANDBY_RE = re.compile(r'device is in (sleep|standby)\w* mode')

def parse_smart_health(lines):
	"""Extract the health verdict from `smartctl -n standby -H` output.

	>>> parse_smart_health(['SMART overall-health self-assessment test result: PASSED'])
	'OK'
	>>> parse_smart_health(['SMART Health Status: OK'])
	'OK'
	>>> parse_smart_health(['Smartctl open device: /dev/sda failed: Permission denied'])
	'DENIED'
	>>> parse_smart_health(['/dev/sda: Unable to detect device type'])
	''
	>>> parse_smart_health(['Device is in STANDBY mode, exit(2)'])
	'STANDBY'
	"""
	for line in lines:
		line = line.lower()
		if SMART_STANDBY_RE.search(line):
			return 'STANDBY'
		if "health" in line:
			return line.rpartition(':')[2].strip().upper().replace('PASSED', 'OK')
		if "denied" in line:
			return 'DENIED'
	return ''

ALL_OUTPUT_FIELDS = ["NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD", "READ", "WRITE"]

def resolve_output_fields(output, exclude):
	"""Selected columns in order: -o (every column for "all") minus -x.
	Unknown names are reported on stderr and dropped.

	>>> resolve_output_fields('all', 'uuid, LABEL')[:5]
	['NAME', 'FSTYPE', 'SIZE', 'FSUSE%', 'MOUNTPOINT']
	>>> 'UUID' in resolve_output_fields('all', 'uuid, LABEL')
	False
	>>> resolve_output_fields('name, size', '')
	['NAME', 'SIZE']
	"""
	if output == "all":
		output_fields = list(ALL_OUTPUT_FIELDS)
	else:
		output_fields = [x.strip().upper() for x in output.split(',')]
		for field in output_fields:
			if field not in ALL_OUTPUT_FIELDS:
				print(f"Ignoring invalid output field: {field}.", file=sys.stderr)
		output_fields = [f for f in output_fields if f in ALL_OUTPUT_FIELDS]
	if exclude:
		exclude_fields = [x.strip().upper() for x in exclude.split(',')]
		for field in exclude_fields:
			if field in output_fields:
				output_fields.remove(field)
	return output_fields

def keep_fstype(device_name, fstype, formated_only, show_squashfs):
	"""Row filters that only need the filesystem type, checked before the
	costly statvfs/sysfs reads: -F drops unformatted entries, and squashfs
	loop images are hidden unless --show_squashfs.

	>>> keep_fstype('/dev/sda1', '', True, False), keep_fstype('/dev/sda1', 'ext4', True, False)
	(False, True)
	>>> keep_fstype('/dev/loop0', 'squashfs', False, False), keep_fstype('/dev/loop0', 'squashfs', False, True)
	(False, True)
	"""
	if formated_only and not fstype:
		return False
	return show_squashfs or not is_squashfs_loop(device_name, fstype)

def df_use_percent(used_bytes, avail_bytes):
	"""FSUSE% like GNU df Use%: used / (used + avail for non-root), rounded
	up when not exact (coreutils-style); N/A when there is no space at all.

	>>> df_use_percent(350, 650), df_use_percent(1, 2), df_use_percent(0, 0)
	('35%', '34%', 'N/A')
	"""
	fs_denom = used_bytes + avail_bytes
	if fs_denom <= 0:
		return "N/A"
	pct = (used_bytes * 100) // fs_denom
	if (used_bytes * 100) % fs_denom:
		pct += 1
	return f"{pct}%"

def format_size(size_bytes, print_bytes, use_1024):
	"""SIZE cell: raw bytes with -b (and for -J), else human-readable.

	>>> format_size(1536, True, True), format_size(1536, False, True), format_size(1500, False, False)
	('1536', '1.50 KiB', '1.50 KB')
	"""
	if print_bytes:
		return str(size_bytes)
	return multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'

def format_rate(bytes_per_sec, print_bytes, use_1024):
	"""READ/WRITE cell: raw bytes/s with -b (and for -J), else human-readable.

	>>> format_rate(2048, True, True), format_rate(2048, False, True)
	('2048', '2 KiB/s')
	"""
	if print_bytes:
		return str(bytes_per_sec)
	return multiCMD.format_bytes(bytes_per_sec, use_1024_bytes=use_1024, to_str=True, str_format='.0f') + 'B/s'

def filter_rows(rows, filter_patterns, invert_match):
	"""Keep the header and the rows where any cell matches a pattern (or
	where none does, with invert_match).

	>>> rows = [['NAME', 'FSTYPE'], ['sda1', 'ext4'], ['sdb1', 'xfs']]
	>>> filter_rows(rows, ['ext'], False)
	[['NAME', 'FSTYPE'], ['sda1', 'ext4']]
	>>> filter_rows(rows, ['ext'], True)
	[['NAME', 'FSTYPE'], ['sdb1', 'xfs']]
	"""
	pattern = compile_filter_pattern(filter_patterns)
	return [rows[0]] + [row for row in rows[1:] if any(pattern.search(field) for field in row) != bool(invert_match)]

def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, 
					formated_only=False, show_zero_size_devices=False,show_squashfs=False,pseudo=False,tptDict=None,
					full=False,active_only=False,output="all",exclude="",
					filter_patterns=None,invert_match=False,match_devname_only=False,timeout=None,
					debug=False):
	global _DEBUG_MODE
	if debug:
		_DEBUG_MODE = True
	if tptDict is None:
		tptDict = {}
	# One deadline for the whole refresh: a smartctl stuck in D-state on a dying
	# disk can't be killed, so waiting `timeout` per partition would add up.
	deadline = time.monotonic() + timeout if timeout else None
	output_fields = resolve_output_fields(output, exclude)
	if not output_fields:
		print("No valid output fields specified.", file=sys.stderr)
		return []
	output_list = [output_fields]
	output_fields_set = set(output_fields)
	# Filters may need data that isn't a displayed column (-F needs FSTYPE).
	collect_fields = (output_fields_set | {'FSTYPE'}) if formated_only else output_fields_set
	macos_info = {}
	if IS_DARWIN and {'SIZE','FSTYPE','UUID','LABEL','MODEL','SERIAL','DISCARD'}.intersection(collect_fields):
		macos_info = get_macos_diskutil_info(timeout=timeout if timeout else 4)
	if (not IS_DARWIN) and LSBLK_FIELDS.intersection(collect_fields):
		lsblk_cmd = 'lsblk -b -n -p -o NAME,SIZE,FSTYPE,UUID,LABEL,MODEL,SERIAL -P'
		lsblk_result = multiCMD.run_command(lsblk_cmd, timeout=timeout, quiet=True, wait_for_return=False, return_object=True)
	block_devices = get_blocks()
	for stale_device in [k for k in tptDict if k not in block_devices]:
		del tptDict[stale_device]
	smart_infos = {}  # None: an earlier smartctl on that disk is still stuck, so none was started
	smart_status = {}
	stuck_disks = None
	for block_device in block_devices:
		if 'SMART' in output_fields_set and SMARTCTL_PATH:
			parent_name = get_partition_parent_name(block_device)
			if has_smart(parent_name):
				if parent_name not in smart_infos:
					if stuck_disks is None:
						stuck_disks = find_stuck_smartctl(timeout) if timeout else set()
					if os.path.realpath(parent_name) in stuck_disks:
						smart_infos[parent_name] = None
					else:
						smart_infos[parent_name] = multiCMD.run_command(f'{SMARTCTL_PATH} -n standby -H {parent_name}',timeout=timeout,quiet=True,wait_for_return=False,return_object=True)
		if block_device not in tptDict:
			if IS_DARWIN:
				tptDict[block_device] = get_read_write_rate_throughput_iter(block_device)
			else:
				sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(block_device))
				tptDict[block_device] = get_read_write_rate_throughput_iter(sysfs_block_path)
	mount_table = parseMount()
	target_devices = set(block_devices)
	if pseudo:
		target_devices.update(mount_table.keys())
	if filter_patterns and match_devname_only:
		pattern = compile_filter_pattern(filter_patterns)
		filtered_devices = set()
		for device in target_devices:
			match = pattern.search(device) or pattern.search(get_mapper_path(device))
			if (match and not invert_match) or (not match and invert_match):
				filtered_devices.add(device)
		target_devices = filtered_devices
	target_devices = sorted(target_devices, key=natural_sort_key)
	uuid_dict = {}
	if 'UUID' in output_fields_set:
		uuid_dict = build_symlink_dict("/dev/disk/by-uuid")
	label_dict = {}
	if 'LABEL' in output_fields_set:
		label_dict = build_symlink_dict("/dev/disk/by-label")
	fstype_dict = {}
	size_dict = {}
	model_dict = {}
	serial_dict = {}
	if (not IS_DARWIN) and LSBLK_FIELDS.intersection(collect_fields):
		lsblk_result.thread.join(timeout)
		if lsblk_result.returncode == 0:
			populate_lsblk_dicts(lsblk_result.stdout, collect_fields, uuid_dict, fstype_dict, label_dict, size_dict,
								model_dict=model_dict, serial_dict=serial_dict)
	if IS_DARWIN:
		for devname, info in macos_info.items():
			if 'UUID' in output_fields_set and info.get('UUID'):
				uuid_dict[devname] = info['UUID']
			if 'FSTYPE' in collect_fields and info.get('FSTYPE'):
				fstype_dict[devname] = info['FSTYPE']
			if 'LABEL' in output_fields_set and info.get('LABEL'):
				label_dict[devname] = info['LABEL']
			if 'SIZE' in output_fields_set and info.get('SIZE_BYTES'):
				size_dict[devname] = info['SIZE_BYTES']
	for device_name in target_devices:
		if mounted_only and device_name not in mount_table:
			continue
		if active_only and device_name not in tptDict:
			continue
		device_properties = defaultdict(str)
		device_properties['NAME'] = display_device_name(get_mapper_path(device_name), full)
		# fstype, size, fsuse%, mountpoint, rtpt, wtpt, lable, uuid are partition specific
		# smart, model, serial, discard are device specific, and only for block devices
		# fstype, size, fsuse%, mountpoint does not require block device and can have multiple values per device
		if is_block_device(device_name):
			parent_name = get_partition_parent_name(device_name)
			if 'MODEL' in output_fields_set or 'SERIAL' in output_fields_set:
				if IS_DARWIN:
					di = macos_info.get(parent_name or device_name, {})
					device_properties['MODEL'] = di.get('MODEL', '')
					device_properties['SERIAL'] = di.get('SERIAL', '')
				else:
					# Prefer udev values from lsblk (full model, real serial); sysfs only
					# has the 16-byte SCSI model and falls back to the WWN for serial.
					parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
					sysfs_model, sysfs_serial = read_model_and_serial(parent_sysfs_path)
					device_properties['MODEL'] = model_dict.get(parent_name) or sysfs_model
					device_properties['SERIAL'] = serial_dict.get(parent_name) or sysfs_serial
			if 'DISCARD' in output_fields_set:
				if IS_DARWIN:
					di = macos_info.get(parent_name or device_name, {})
					device_properties['DISCARD'] = di.get('DISCARD', 'N/A')
				else:
					parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
					device_properties['DISCARD'] = read_discard_support(parent_sysfs_path)
			if parent_name in smart_infos:
				if parent_name not in smart_status:
					smart_info_obj = smart_infos[parent_name]
					if smart_info_obj is not None:
						smart_info_obj.thread.join(_remaining(deadline))
					if smart_info_obj is None or smart_info_obj.thread.is_alive():
						smart_status[parent_name] = 'TIMEOUT'
					else:
						# smartctl answered but gave no verdict (RAID HBA, unsupported device).
						smart_status[parent_name] = parse_smart_health(smart_info_obj.stdout) or 'UNKNOWN'
				device_properties['SMART'] = smart_status[parent_name]
			elif 'SMART' in output_fields_set and not SMARTCTL_PATH and has_smart(parent_name):
				device_properties['SMART'] = 'NO SMARTCTL'
		if device_name in tptDict:
			try:
				read_bps, write_bps = next(tptDict[device_name])
				if active_only and read_bps == 0 and write_bps == 0:
					continue
				device_properties['READ'] = format_rate(read_bps, print_bytes, use_1024)
				device_properties['WRITE'] = format_rate(write_bps, print_bytes, use_1024)
			except Exception as e:
				debug_exc('throughput format', e)
				device_properties['READ'] = ''
				device_properties['WRITE'] = ''
		if device_name in label_dict:
			device_properties['LABEL'] = label_dict[device_name]
		if device_name in uuid_dict:
			device_properties['UUID'] = uuid_dict[device_name]
		mount_points = mount_table.get(device_name, [])
		if best_only:
			if mount_points:
				mount_points = [sorted(mount_points, key=lambda x: len(x.MOUNTPOINT))[0]]
		if mount_points:
			for mount_entry in mount_points:
				device_properties['FSTYPE'] = mount_entry.FSTYPE
				if not keep_fstype(device_name, mount_entry.FSTYPE, formated_only, show_squashfs):
					continue
				device_properties['MOUNTPOINT'] = mount_entry.MOUNTPOINT
				statvfs_wait = None if deadline is None else max(_remaining(deadline), STATVFS_MIN_WAIT)
				usage = get_statvfs_use_size(device_properties['MOUNTPOINT'], timeout=statvfs_wait)
				if usage is None:
					# Hung network mount: always show it, it's what you'd want to see.
					device_properties['SIZE'] = ''
					device_properties['FSUSE%'] = 'TIMEOUT'
					output_list.append([device_properties[output_field] for output_field in output_fields])
					continue
				size_bytes, used_bytes, avail_bytes = usage
				if size_bytes == 0 and not show_zero_size_devices:
					continue
				device_properties['FSUSE%'] = df_use_percent(used_bytes, avail_bytes)
				device_properties['SIZE'] = format_size(size_bytes, print_bytes, use_1024)
				output_list.append([device_properties[output_field] for output_field in output_fields])
		else:
			device_properties['FSTYPE'] = fstype_dict.get(device_name, '')
			# fstype_dict only holds non-empty types. Squashfs hiding is best effort
			# here: it is only filled when FSTYPE is collected (an output column or -F).
			if not keep_fstype(device_name, device_properties['FSTYPE'], formated_only, show_squashfs):
				continue
			if IS_DARWIN:
				size_bytes = size_dict.get(device_name, macos_info.get(device_name, {}).get('SIZE_BYTES', 0))
			else:
				size_bytes = size_dict.get(device_name)
				if size_bytes is None:
					size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			device_properties['SIZE'] = format_size(size_bytes, print_bytes, use_1024)
			output_list.append([device_properties[output_field] for output_field in output_fields])
	if filter_patterns and not match_devname_only:
		output_list = filter_rows(output_list, filter_patterns, invert_match)
	elif invert_match and not filter_patterns:
		# if no patterns but invert_match is set, return only header (with or without -D)
		output_list = [output_list[0]]
	return output_list


def printable(text):
	r"""Escape non-printable characters (ESC, BEL, newline, bidi overrides...)
	as \xNN / \uNNNN so labels, models and mount paths, which anyone with a
	USB stick can set, can't drive the terminal or fake table rows.

	>>> printable('pwned\x1b[2J')
	'pwned\\x1b[2J'
	>>> printable('/mnt/a b')
	'/mnt/a b'
	"""
	if text.isprintable():
		return text
	escaped = []
	for c in text:
		code = ord(c)
		if c.isprintable():
			escaped.append(c)
		elif code < 0x100:
			escaped.append('\\x%02x' % code)
		elif code < 0x10000:
			escaped.append('\\u%04x' % code)
		else:
			escaped.append('\\U%08x' % code)
	return ''.join(escaped)

def drop_empty_columns(rows):
	"""Remove columns whose value is empty in every data row (e.g. LABEL when
	no filesystem is labelled, SMART without smartctl). A header-only table is
	returned unchanged.

	>>> drop_empty_columns([['NAME', 'LABEL', 'SMART'], ['sda1', '', 'OK'], ['sda2', '', '']])
	[['NAME', 'SMART'], ['sda1', 'OK'], ['sda2', '']]
	>>> drop_empty_columns([['NAME', 'LABEL']])
	[['NAME', 'LABEL']]
	"""
	if len(rows) < 2:
		return rows
	keep = [i for i in range(len(rows[0])) if any(str(row[i]).strip() for row in rows[1:])]
	return [[row[i] for i in keep] for row in rows]

def _parse_percent(value):
	"""FSUSE% cell to an int percent, or None for '', N/A or TIMEOUT.

	>>> _parse_percent('35%'), _parse_percent('N/A'), _parse_percent('TIMEOUT')
	(35, None, None)
	"""
	return int(value[:-1]) if value.endswith('%') and value[:-1].isdigit() else None

# --check: the columns it looks at, SMART values that are fine ('' = virtual
# device with no SMART, STANDBY = spun down, checked when next awake), and
# SMART values that mean the disk wasn't checked.
CHECK_FIELDS = ('FSUSE%', 'SMART')
SMART_HEALTHY = ('', 'OK', 'STANDBY')
SMART_UNKNOWN = ('NO SMARTCTL', 'UNKNOWN', 'DENIED')
# --check exit status, Nagios-style: problems beat unknowns.
CHECK_OK, CHECK_PROBLEM, CHECK_UNKNOWN = 0, 1, 3
EXIT_PIPE_CLOSED = 141  # the reader went away (`statblk | head`): 128 + SIGPIPE, as a shell reports it

def check_rows(rows, max_use):
	"""Return (rows to report, exit status) for --check.

	A problem (status 1) is SMART that isn't healthy or unknown (FAILED!,
	vendor failure text, a hung smartctl), FSUSE% at or above max_use, or a
	mount that timed out. Otherwise SMART that couldn't be read (status 3)
	is reported, since a blank result would hide that the disk wasn't checked.
	A check whose column is missing (excluded with -x) is skipped.

	>>> rows = [['NAME', 'FSUSE%', 'SMART'], ['sda1', '42%', 'OK'], ['sda2', '95%', 'OK'], ['sdb', '', 'UNKNOWN']]
	>>> check_rows(rows, 90)
	([['NAME', 'FSUSE%', 'SMART'], ['sda2', '95%', 'OK'], ['sdb', '', 'UNKNOWN']], 1)
	>>> check_rows([rows[0], rows[1], rows[3]], 90)
	([['NAME', 'FSUSE%', 'SMART'], ['sdb', '', 'UNKNOWN']], 3)
	"""
	if not rows:
		return rows, CHECK_OK
	header = rows[0]
	use_i = header.index('FSUSE%') if 'FSUSE%' in header else None
	smart_i = header.index('SMART') if 'SMART' in header else None
	def row_status(row):
		if use_i is not None:
			pct = _parse_percent(row[use_i])
			if row[use_i] == 'TIMEOUT' or (pct is not None and pct >= max_use):
				return CHECK_PROBLEM
		if smart_i is not None and row[smart_i] not in SMART_HEALTHY:
			return CHECK_UNKNOWN if row[smart_i] in SMART_UNKNOWN else CHECK_PROBLEM
		return CHECK_OK
	statuses = [row_status(row) for row in rows[1:]]
	reported = [header] + [row for row, st in zip(rows[1:], statuses) if st != CHECK_OK]
	if CHECK_PROBLEM in statuses:
		return reported, CHECK_PROBLEM
	return reported, CHECK_UNKNOWN if CHECK_UNKNOWN in statuses else CHECK_OK

def rows_to_objects(rows):
	"""Turn get_drives_info(print_bytes=True) rows into one dict per row, with
	SIZE/READ/WRITE as integer bytes and FSUSE% as an integer percent (None
	when empty, N/A or TIMEOUT).

	>>> rows_to_objects([['NAME', 'SIZE', 'FSUSE%'], ['sda1', '1000', '35%'], ['sda2', '', 'N/A']])
	[{'NAME': 'sda1', 'SIZE': 1000, 'FSUSE%': 35}, {'NAME': 'sda2', 'SIZE': None, 'FSUSE%': None}]
	"""
	if not rows:
		return []
	objects = []
	for row in rows[1:]:
		obj = {}
		for field, value in zip(rows[0], row):
			if field in ('SIZE', 'READ', 'WRITE'):
				value = int(value) if value.isdigit() else None
			elif field == 'FSUSE%':
				value = _parse_percent(value)
			obj[field] = value
		objects.append(obj)
	return objects


def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.",
		epilog="READ/WRITE: the first query shows each device's since-boot average (bytes / time spent on I/O, idle time left out), i.e. its typical work pattern, not a real-time rate; later watch refreshes show live rates.")
	parser.add_argument('-j','--json', help="Produce JSON output (list of rows, header first)", action="store_true")
	parser.add_argument('-J','--json_objects', help="Produce JSON output as a list of objects with numeric SIZE/READ/WRITE (bytes) and FSUSE%% (percent)", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (read/write activity since boot on the first query, during the last interval on later watch refreshes)", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2)", default=2, type=float)
	parser.add_argument('-w','--watch', metavar='SECONDS', type=float, default=None,
						help="Repeat output every SECONDS (watch mode). Equivalent to a trailing integer positional.")
	parser.add_argument('--check', help="Health check: print rows with a problem (SMART failing, FSUSE%% >= --max_use, hung mount; exit 1) or unreadable SMART (exit 3), else print nothing and exit 0", action="store_true")
	parser.add_argument('--max_use', metavar='PCT', type=int, default=90, help="FSUSE%% at or above which --check reports a filesystem (default: 90)")
	parser.add_argument('--sudo', help="Run commands as root with sudo. Needed for querying SMART info.", action="store_true")
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('--show_squashfs', help="Show squashfs images on loop devices (snaps, AppImages), hidden by default", action="store_true")
	parser.add_argument('--show_empty_columns', help="Keep table columns that are empty for every row (hidden by default unless named in -o)", action="store_true")
	parser.add_argument('-D','--match_devname_only', help="Change filter pattern to match just the device names instead of the full line", action="store_true")
	parser.add_argument('-v','--invert_match', help="Invert the filter match", action="store_true")
	parser.add_argument('--debug', help="Print suppressed exceptions to stderr for troubleshooting", action="store_true")
	parser.add_argument('filter_patterns', nargs='*', help="Filter pattern(s) to match (e.g., sda, nvme0n1p1, btrfs). A trailing integer is treated as --watch SECONDS; append 0 to filter a number without watching.")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")
	try:
		import argcomplete
		argcomplete.autocomplete(parser,always_complete_options='long')
	except ImportError:
		pass
	args = parser.parse_args()
	tptDict = {}
	# Prefer explicit -w/--watch; otherwise peel a trailing integer from positionals
	# (historical: `statblk sda 5` / `statblk 5`).
	if args.watch is not None:
		print_period = args.watch
	else:
		print_period = 0
		if args.filter_patterns:
			try:
				print_period = int(args.filter_patterns[-1])
				args.filter_patterns = args.filter_patterns[:-1]
			except Exception:
				pass
	if args.check:
		if print_period > 0:
			parser.error("--check runs once and can't be combined with --watch or a trailing interval")
		# Show why each row failed; -x SMART / -x FSUSE% turns that check off.
		if args.output != "all":
			named = {x.strip().upper() for x in (args.output + ',' + args.exclude).split(',')}
			args.output += ''.join(',' + field for field in CHECK_FIELDS if field not in named)
	multiCMD.set_sudo(args.sudo)
	# multiCMD's quiet=True hides its "Command path not found" line, so say why lsblk's columns may be incomplete.
	lsblk_note = LSBLK_MISSING_NOTE if not IS_DARWIN and not shutil.which('lsblk') else ''
	# A terminal is redrawn in place (one write, so no flicker); piped output and JSON keep every refresh.
	redraw = print_period > 0 and sys.stdout.isatty() and not (args.json or args.json_objects)
	check_status = CHECK_OK
	try:
		while True:
			results = get_drives_info(print_bytes = args.bytes or args.json_objects, use_1024 = not args.si, 
								mounted_only=args.mounted_only, best_only=args.best_only, 
								formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
								show_squashfs=args.show_squashfs,
								pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,
								output=args.output,exclude=args.exclude,
								filter_patterns=args.filter_patterns,invert_match=args.invert_match,match_devname_only=args.match_devname_only,
								timeout=args.timeout,debug=args.debug,
								)
			if args.check:
				results, check_status = check_rows(results, args.max_use)
			# Only say why lsblk's columns may be incomplete when the output has rows and shows one of them.
			note_due = bool(lsblk_note and sys.stderr is not None and len(results) > 1 and LSBLK_NOTE_FIELDS.intersection(results[0]))
			if args.json_objects:
				import json
				# Watch mode streams NDJSON: one compact document per refresh.
				print(json.dumps(rows_to_objects(results), indent=None if print_period > 0 else 1),flush=True)
			elif args.json:
				import json
				print(json.dumps(results, indent=None if print_period > 0 else 1),flush=True)
			elif not args.check or check_status != CHECK_OK:
				# Hide all-empty columns only for the default column set: an explicit
				# -o asked for them, and JSON keeps a stable schema for scripts.
				if args.output == "all" and not args.show_empty_columns:
					results = drop_empty_columns(results)
				# JSON output is already escaped by json.dumps; the table is not.
				safe_rows = [[printable(str(value)) for value in row] for row in results]
				table = multiCMD.pretty_format_table(safe_rows,full=args.full)
				if print_period > 0:
					header = f"Every {print_period:g}s on {socket.gethostname()}: {time.strftime('%Y-%m-%d %H:%M:%S')}"
					clear = '\033[H\033[J' if redraw else ''
					table = f"{clear}{header}\n{table}"
				print(table,flush=True)
			if note_due:
				print(lsblk_note, file=sys.stderr, flush=True)
				if not redraw:
					lsblk_note = ''  # once per run, unless the next redraw wipes it
			if print_period <= 0:
				break
			time.sleep(print_period)
			# Throughput is always 0 on macOS, so active_only would hide every row.
			# Devices named by filter patterns stay on screen even while idle.
			if not IS_DARWIN and not args.filter_patterns:
				args.active_only = True
	except KeyboardInterrupt:
		return 130
	except BrokenPipeError:
		# Reader went away (e.g. `statblk 1 | head`). Point stdout at devnull so the
		# interpreter's exit-time flush doesn't raise a second BrokenPipeError.
		try:
			devnull = os.open(os.devnull, os.O_WRONLY)
			os.dup2(devnull, sys.stdout.fileno())
		except (OSError, ValueError):
			pass
		return EXIT_PIPE_CLOSED
	# --check: silent exit 0 when healthy, so cron only mails on problems.
	return check_status or None


if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == '--doctest':
		import doctest
		sys.argv.pop(1)
		result = doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
		sys.exit(0 if result.failed == 0 else 1)
	sys.exit(main())