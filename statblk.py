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
import functools
import os
import re
import shutil
import socket
import stat
import sys
import threading
import time
import traceback
import typing
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 51):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE$ig8-O-i5'i+r01HsH^aLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)d^;Cl"iF+?;5$GY\@0&f>,"jBk/
YiH%6+MO0G/&_cVMbEIV%te4SsUIN@I9"V,DPig_^G):A?gs:G4WIo4U9V(ca0E&!d7=Dp]k!,Ha*Kah\qE4^ZV8^P$l@o]F\b'NLI.UoSLB2-BsAPK<
TC+)/F=9lUh$$,-L0U,\B$Beq)E4d*p3?al3[\ThsBL1lSo.bKBCPcZ<_?NmrNo)ZLj0,OEjn[/cE:Vptg0[Cq7Wfn#8`N8iGq@':[%E_d<[n<Da,s![
V)Tt+8:H>-U",1)'J#^*$DjC3hYHqso>I7'F)4%WckpDf5TQ[U>Pk,]P^C%M?]kDI/O16EW_.512+,N&D1#T:M<Me?X8f!KNEY"U?8EDPpeDJ;-.&W;?
-326YM;Q9M/&S.GMTP2c@aHA+L.,7!!]lK=G"2A9$Mn#i)90BAG\g`*=3<p@:IY(m8,"V^d3PJT@K]W@?A\!W6kH"hmEp.8DK*R_ohW,n+I7QR*Sfb+L
S5(D&1#C.%&r%+^HcL(J5*YnF0MA+4SHl8QPl4V@UCUFk<QC'@&7UcN*cu]g&F@0od<6jU``WZ,a:MLcSb8BA(%3QN`>>H+DC$,5K+8TK7<BO`@;aZ*[
?6L7CjnGCER'7]CXE_\_"<1M:InKkKGE>AlM%"EQ5P_'Y,t[&FsU<a/WOBAb4mdU+&c"$n^gPqMbZN?PoQE'gc^fHX_(R#,:;:[WKZ%<P53`fY>X>%24
u4,L;!3R>]4+n:7,9,VpcVc8_qP0=RNh2o\J+1jDoXmGcRr2YE4QRW;i7m8kmseZsr-"N>-E^_rhp(WM)\dh[M+`mX;]sW!dtj6bQ"$]rTjs71\k6@ik
V'EX!9N?-j"Fa'NG#r8T-L9QP3mSDPMkp2BpSM4>U/:.(mHbA+H)IeP9a4lAQmNT,S>j+(U`+.%p]g[_gP<ol;a?brX'Uhf9"@l_OA@(>>DF$Qp)q5<J
L4L%tG>WsXg0hYG8ODMFCBedZHSjg'7/('>=6^F2t[dT*0@XGshE*Qb">Zn@MEqNEA,W)Jhq.=:\DFJ$5X.P(2c0oWAM)sCQX4a+ppLYRu*C$a?-`)"t
heej,p1^sE4khB@M%@6Ao`I\PF5E6X@Km;Q>J4%gQXdf8rVp>X@e]/E&?u,o@mq!8N=S*?/9=H2GO+)g5%?*oAkVp_ba3V$Wiqn2ck^*?Y`*W:,%tRoj
2T"P*^jp:Z2%S2ocM95+GuT9D^C5?)k<)m?cFn4Xha^NL;Ym(2^uH%2R8e?,@_K%X6QSO.Kg@N[3B8(Xe_?SDDk><B5..I2r.b$"K!Ei'[A20o"QDaOW
4W4fGRBSGM>M^CddKF#LT_$eYk?70p+rq)ems(WKCVmWG>VPoai[<?h@T#feB`?+WkMqh,E-oQ`Ir>fol>(qYcpedQ1[Ul:=%Yj`kpmB!]$^fZZ@J']<
;4&ujr7fOlB@R@P>pf8]k7I-,i8gml7j.sEb4T=F3H/s9E47sPPU\o/JT\huWtebQVX9HYmD-eA)-IX>?OY)TpW2JL+S]`qtMP%MNM#fAG8*SmZd`:*e
),dK9+bNAL.IEWbsbk&Qd*6)`['\Bgk5XMQje1oqh*2D\@!CXk8[!"/:<^F$.?"m<QVPQs+s)Zc$n6+;Zr3UBma$.`0@*^8/')/tS*[Z$tqC*pH0$;8S
^gi9el!6%oqNHejC;*U)7))l1cOXd38%'Tp+WN=WI9QV'1@S;d'Y`(]S"iQ\.H4OVgFrjo_l0L=8"oA0-5'@$#Tjk2j@?IG/?GQB]rtATb#F'^>S+,eU
>EG^$+?01'Ntu#D`fM_,6=KQ&j9d>GI:j]U':WMe$<t%9H6LoqMJ^c@pb/(`DomO5Q#f8o@Z+/G2i)HnC[b2ElL)(=Yk/m__&QOhK_iE*%<b[XfaqBI!
o9&^DQ.nhOgI9`Y6V`D$Q<AjOEg=>M=TP44pk8R%\&J)Pc&23"I=.(k8g9931T.4DUP4h\2pOCG#WZV4)FNq5KZ\n+[eB;r?mU`\c;6(l!IQFeCJmc__
@Qr(';0WIY:j;u#<UUh&':1Y%PI'K)TD-2$3`0o?G7!deqi>OO-?X`,g?4DUY,o5;@;a&*\)p,Nk4OYHLR?m)`e/nPqS`Nbu;Tpd^Y"jErD10E5V:H*n
en;qR3^UkjT&)HY7H@[oe0@)=dg./)Q4>=g9c(,OjS>>ImG&Db%3:11Noe3[g%8p4(j)1Fnh',L*UZMaV'%Ea)Pd'*Bl/#KTMb)2p%gI@cFpR5MEslcf
\!#^uO3@eXeI/]0!+8;mY[c/4`]@8&7sH5fZ-,H@!78MQ7sa`l#m+&bHrj=.5^0Sc_hnQ.X6<S)]sl"W(Ji/a0ro#DBMdSaE9Uis#b.i]ITCL5#`oR7)
sU>*Ft]Q*QW/8%?mHW?OrYce_pSi#'*bDO<j=rH>dCMf[RPUgOZU(`DDu^+5,gh0qQp^uYKI0p9c;`Onho*d\CpR2dn3S"4]7KPREE5a<J&o(E"lUh&a
Jq%chOD1I_6"j>QNkWQYfPc:mVl-Kj/]^;-^O$kp`?1$g.MNRO!O>]Y-V4EYn>!/Ij4%i43\[Nd/NK65B\]Q+p?/%_u($_mdP5\I#Il35S5Z.*i="60i
Kg]Z1mc5)6AD3EDR->j8)N[qe4=eM?9C]%4W\0p3E95it<&#`)sk#HoZEHJIh!LecRIf9McY+^)m5#fI:0GqifK=PX3TjX9!#Z\-3>b[LP!+?)gJ>D2?
fN`u@pW2T5T*7]#7+B:*nk7DL/E6&XO_Nq;P>#&Hd6hcB"UZ9PN)t=sX%ZB$YI,@WO?o\B<?TR6;TL>R$g+@cPGjQmr199QeK4Kg]fS\YN!]-Si(BJk\
GanO#;c73L.XZA`_G4jNIo@<D4NVl<7O@&]EB?t<l)QjJ+L&!:VJ*-+Fe!].,$u7WkD4s4qOK;_BnumShGbhd!lFSj1CYc;M<iZVe,o^q@B`77p]aA*6
_M'5+tK,!]?!/s=inj$qj!Fpftfq!Nq?QZ\7sMrj67Wfr=Q?1pFP[r<Q%+u1-3bs!W*/$jp)Ep#3.Q=q+gQCmh9S?7(hp4JbbmH[brq4&^RpU^mT]gi<
'3bkdnnUNhZ<L\jo>p9H@F$=K!j1-2OK?;cKeL)sZc9d,a9%IBI1)EVkQsqos4"X>bh0KZS>=@G@pCa;*u6,p"maoU41F`;j?a(o\GQC`H/pfQ/2g0a7
SWU-ogXZLb+e$D7ToI8R^D7B9hT;:6Z[I_.CYlgXl#&@@t9Vr't)(7s13-'6ieK8CJDJ;LuWe`0cs,kp(n"&"pf=R0'q?pm&lbiRfu:$q=if#/YR0`?H
]F7!;R@n>QAmFCopc3/6ES6CR(PYfM"I4VdVP@I.P7m"@_-O?qkCXM^p(dm#7h&H1J<f8l7a0fabMSfWd_T[uBYB0St_#!)KY;N<N,Kd03a?87=.guQG
1TM6!9HN;u]0>F:]\%oH2082]@!k$ERMbu!Z&9bPF!H]Q8T(0G,sfi,.ORL66:"N-'CWYV$7+o=A+/'M1I-'XE9g0P\poHKSc.-0F0""Mphb7a0j9O>T
G=_,67d-Q"cGed2cnq%/uS7,iT2C^DJWCL&<9D&D.63ph.LMh/MKo)<1J_;T,/$sYGIFu7RrnIA&f5%*iR[iRops8>+IdJ&Wk);J"S2;fd`+_DJDWUg(
p3X,JdXLLF\SX(o$2\SS+nbh+P;W6-b-5N8O(11Jsg\b?Y3.OoBXdjZIZ$;b%84/'5jE#9nijE(`Q=0L9L`ViS7QT#3JjBTH%!/")19,pd%^kstW'dJI
$l^ILddi_JA"cCbRnr=nQ1[?q(KN7@-&ONu5VH'5Rp*Ql_(5</\Z*O_!H>`-4Q3b%)haV=:b.e]#cL?pT$#:Enf&ZoMrrSYYf^bu7uY:819Mt`gGWBB?
@&ZQK"dq(R_Ug1d!+YQkI>^0!\Og[gBM&\j`Qti/,_f"f+(V)i]B/<?W-]>9#'ff8@bB-,A;L)L>&9Tq;DEfXD_^_7I"aTNrQ<O3d5gr=?>dShPTt9TP
#gg#RD-GI\@Q#c-ELRE//Qo$'+^,c(2XG6]NNq2jCJoq2CLG3IJu!TiVQRBLpuKS.&V>6*AVm1:+=j5C]*5[b)Wm:*<6$WLjj^U&p8&@TQetCXW$+2_A
"SQrR8P=L+_/f'WZQICBNkQk9uM^Z\jZe/Rf.b$l"c"I>Wk\=X-PIt&Kc\2prh-Ce<bgk4us-Lc^&t#'U7bP%BETUNSPoH^1bhBEi3?)?%YL7PXDD'P>
):@]ZqUcO!DNn*9&qNq!s>KcJlGppY.hUc87IM]cmJ!#2*6;9FJod*r1EnO<`l0:;L;7:)4XqHgf3q7mKuG_H..Ch_U(kV]<;<C5kg3JN2h*aN+qtfde
/`KSiTliQAMaK(AfLkA-n&I,T11VIWHe?r;'19LK7SrcKil-j>Z?pH&_H)Xo_C*SIXFS,`>'`8=W)d"Z_"b@VHTRu#]*W4aZJ;Q/R]2N9Ma#$8ttU;,^
@XNk460U_;E"3htH"26=SRFph9WCq?;jEm=^l?Fbi:=^.O@G)^W&*ME:jkQIJ*JnDE)9.;BVHX$:]Q]K3oMNTTYH!tf,i!"K+!<</H!p-G'5saD6M&b8
1]^dhXZ>>mrf$G]E)D$]8LeUt02l83![>2Y+O7\68C`>5_Rc&3#-kA$n:R='],b>\@8:ns&+3X?Zr#Y1=5U`,c5I%5,)QLV4Wp:G5;jnimndrI<tIpJ6
$?biZk^Z:g>0+HK%#58D,?gQ88#uRY-iVs%]-m(6lgd0oFP[T-e:)#$-rRUIODoA!";!76[7M6jL(K*rA63^HXikX@Tj"?^4JU^%D'b>FV.u5.pEb`Z=
L)'(JXo>HE:M`2-qX9FA\44Kp"tD)(4"q8T>s37t7rITW_Y*-D<^<1g&qVUg%GBNs0gJaK4.^B0#04Cll'2C=Nl?H3ch!KBq3-'Dg'qL#]j(j_%6%c*\
g>Gfl!0=\MY=1\Z8NcJP>eYpEaA<gLcU(RL9$TKU)Z2?\B\L.jKNB3V0L,]2s8H/jce_@aBfc!@HVJtj-n#Pp2kl;oZrYG-b)Djn/H0?:UH<nM>U42-Y
qM3H(BPUsE<7/Nq`:JOG5o3j&I0o\+J)#ugSX))AU$q)THd<7L23&u2IH1TJ=QQ*4?B'8iO5otnQ`@0]?1Kf>`Z0jgR@Sm?ZMZ(+T2l:K$Fpbt_O^YSo
^/G7BL#o4CC-I=bB&$FR<)Vc;b?qr^B[=,F2.HX%U5uWmR6S(pF7dN9]IZ7;R/7`J\M*G_l68BoL_N[I\-7]6dN0P_;H@,T'2hu''-<bAm_EO;5?`\ti
OXLS>]P;b["Ul2QgR(n_bXoGh?#;=0aCYO+7Mki-E7a'Uh@"5q[-TP=D#%C3d%)hAs0#;ZY-K*3Cdf':4o"R>J7ilWAgq4E\tasQ--8D"']pa_j,)PkM
bsm^=CfQ71AutU;t=GbV+)dl40bjFQWCB.*8G_,,@c0%KolE%NjI[o6=XEJI8ZE,7su!_o<.D2KP20*bJM03UHLGM]jk#j&I,Do[_)0i/Sk+?dTG6NCf
^(R$Ci_8i[6\aPCf64<TGpi>a7Ib!6oeoFq6h>$aE[gQ24is"<M0ShoMUM)GVS#$\$15U4i0PRsD6dO0sU0.q)$bI1u,o6l&kPfW?"p>_SARL`\PR?1R
5o@Pl"!NtJenU+98.k/r5U1UZ7M,/T3GSG90Nq.+AZtd>oDmre2bS&hnW''H9=OLGSb(DN+$_agg+BPAU+Z$P@Y#0u`b!`BqjK(c-M3'8B]mU*GZ^EY2
,bV727dI"NRl[93o'S*8K@R>-,J.mL8K>t0:Fk5NBr"7)QVGM:p_L(N+TtR/^uHfqqZ'F+*u%Q1*8GT4oZ)SY79/=LSO]F1>f)t<Eu7g$`"(&1k5RZ?`
d,bF_s`rs`l<=NS.$Y!D@keL*pAHGM9Fsr48..sfP+2>;'1%:;77EEB+Rr'/]0SN_\4NZjP"l]a#>t"=Fq.?7BGEM.Uf*ZXA9<k)rlUg(6@'DdkDF3F1
+)qm(DCUmN1l25O[S]%:12CY3ER"afKn"(OGP[?lNiNVuH/O^`E9O0`N(t(mEK;giRBoa87G:/0L"P?MZoel.bRg*JfYY%)61]'^Xtc$k,X\L.#-=;_3
OMHk:(I1_&;K"bU_UYj.r:aV]=r(,"`V@/&%B]8^a6AN5kei_"p5T6kYURGOZ]s,j_J87k$HXY2\qhiK#F>WA-kp&tLioJM&;]KCLF48B)EI'+lpqd>/
nF_lifh'39C7qV=`g!k?i+/B.+g+@@%c%rfrAP;oGAnPl(`_*qaF9!fg<itd`&Xt;Q(S#:m>1W!OE>*OfN^fZ<KG"`c)u+LC/Gq^\K/@]^W\SRa4Y$Am
hMeg"0t=JoqpXRl`E`K[-kh@nOQEp_#pbbIYS#F\&GZ^ejs))]CAjm#5tOF,X5R5SIbL_A0gn,((P?D5@?npXKK[d2q;t1\EGD*g+\7B%Kdm9,<;`d',
><$A3T@Q&U0^@&8(:X?U-#h%DCd4>a0Z[8`CBqk=9L>B_W+AkmfCM^RS?.A0UQ/;lTa]N>j;^n6N:Z\OO<"kHI8aeV\Y"HGZ;XE5Du`58VR"u!Q];XI`
"%2,:u%l`eVtimgc`j+A:D*YRl1JTt+I;EF[b"0_oH+rQ,gaI!WHg5J8?(_WkT7,V+I).+JP:>6u?_UDXrt-Ro`NO&X<,Q.bqd*tJ%kqIf?trIe.!^Y'
Bms+miQk<;!&"[mZj_V"c\->3QYd`N6^C0`FS5.8IZ;CbqVS*K8`_ioo!1CLRKdG2b"3*g!ML.H/;mpXO%S@IF^KE=J"L\DgVO)fdHk,cmSWL!1LnXuo
KaF.9D;Q%^XMP1:PGSOd-;g0]foW%+3/ttgCQ7c0&jDSs_6mt-9i1%&WpRr2K5q6%A$L]d.7Xr&.HDH,]rDMEVs0q9h$0NW.`JtJ8^k1<<Q]dd``d_F-
gP'Gf]t>8TWaX:RP?Xt1YTAfneY<D*5K8\<E*J>u5J^]fI/'cagZ)_Z&U^n(/pHePI*6DhOqMC!/D,lXR0ViO#k]2s,/9/?"9qe6fTQcJ_qLb5L`_e"f
J*%>/D)d*8*qaEEfcI//s\P"(OlN$a=;ntrQIS2KM$s.a=Dqfo;Fm;qpWGYVcKQlqVSlZ)8..<kcWQSb5bi^#Y4drENObuIf*+d2?1h.K%^10cukEoSV
F,Y@hFbHH$%O$JDU.;B&U)AIJ>NX8J7cl'qJ3\D`^*[Um5=(G^0Z>DkGlGo_Nn!&!;7'/H2r0Y)n)nJnMtHf0!P=hf@TE&m(Ip\>^sR;l#K5M^)iZAZ4
*k?AK[G#h'@L,?.hekCiJ#BO-[lZogLl`T$S^Dg$_-9XVM!pbPMANER2`9H$F-C_ZWi;)i"rIY\\7p@;GLF,Hg*Z]A=I]eF7_q=jV<G=Grl4)fo3=<uY
4/#g=<ObXqc?D=>-,,9f/UkV6/h81L]:+8SFBsr\9U"#EM:oG]MUcm5kH[8IiS[i.#A[`?aA:0:>;#<pDK5)l^fWjY<$To:XMFt#Sei=Y?Kc"YdA[)56
gT=%0o(3^JrY0c1bQRqMY;Z)go$c^&VW6c\CNg#&XPrh(nB4u+ltW<J%X']qV]Fc`aU1tEc(V#-\V(CqS1b2GR<D=iZSO$d/'gJJ5kh?<4$.$`IbPe:R
5==iH?U&__&Utl6cE9F5frdBXI#NHUW(JlH\Y$[\HaBe@t).qlC61b9c=8-T;H0&-.`==Jt,Dq_1FK^[j,Jdho@e;KuPm8oG%)X@)&\A.gX6l%:^4,kO
'#^"_CkcLUm6M&t2^`>\b6B*;gMY]<W<0Cq7111'+41eknqg,,F;B=)]8!@AaH_<r?4T>D;EbYm&FWQSC^q$iWNsBZG@a4hf1;8F_P3:)+&F&B^.EL;f
(AdhP2#WF)l`<#bE0\#&IJCU$1K_'K^^4L8Js!3nX?2#@F-eqL.XfJItb64ia\J-$"C;c%)71P0fJ4psK$Yiq]F3.:N;W<6@c/bZ?(-I?Q>]l,T[gRfh
.A0kNfUa.eGEULKtA[_gU#VT.l=]kgfo(uUkHW2^E=jkRS\LkO.+E`E3p&JaZ4e^7Q]c;bj\TiI0H\sETXLMu!_WF(>baf(ZHZ+?T%UL54W'h<[BpUD9
9jIOLDC$]\k+(9r?cCS#lLXJ`?Mb*Dk3M\d%5-c[1e81Cl*[O&?p@?H6]1a^,,N"%J>DRQSd$Uj=mdq_Z$rd>hAnG2O9!6-A7f+M[j"s#&=#!CFbYtrM
'mo-fGT7JTg>^8#(%>pM6^#DHnP]!YbT89j/m=!Z*Z_S]bZGelFlS*&O;RJ'E:.X3=4:E\@o5Kb@fCYN]h=b!t1Nk3rTV)QCpk/*]+.M(KAQM_*6.l\!
`ja9_eH()4*&(0G0oJ]*\1H/t*nLflr_Bqj#PLODig\;1^%i1BWMa<U_gQAr+hOP7kcC/MKg3NG]L974)8t,f<b)J"KV\i,c2[\C6BO'VL2@FI(+@]5'
S@/Mnef:&L'p9;3O\F0,u=(@(>apt#?($GBL!Ya:M%[$i*`NG#'!\),TR+Bh4YTl%h!#iMbIPho%7`Xn/jB@E&n?TYaS)K/G;VqrL^pekNYA'Ll4ZD3R
`ktS[c%r8d.8LGiFGX<i\JZf)7?<S7?@rZ]_%EVeC8nQFF`;E%[eu,<kT9SIV<'!]dFPVL$_EWD-mEA/m.soZ.g+);q%jDSu(QbElb&3K^^chec1$ieA
Htk:%*$g=ji0G$.dnNRE#UH:<DZu9f'a27Rmto0QF!b(WrRO=(q,,N5C=hZ@bgJF&>a5R@ldX/I<Pq155]n<FKQ=&&4@nZ*hqUCFJ`DT=RT.t`LdrO8X
sl'PrQb)rQW,QAmC[DmhX._[cOr1E0<VMP1KLip8Y.qWYMfY7-Sqm"o(>iTp#:lPT"Zc1Ud6S9Y/X.`bBTRZ/d4sNI*Wi@O4=U[W+$KE72+S_o@eY"P\
@^.Q2gDB<;!P`&U-_o?>lAQ)L.$D/o.`r3THQP2RqTPLe65RPtsF]c"[FtoZM%S"tC[)7tq8-T<l/9KH(g1%gM<\*cB*BgXL`?+/s]]#264p5^rQ:s)U
"qbj;Mie!Rq;`87n!Q-D0i?4h=q6[=_YlbC`NO]\luLcY%3:gV(2k45fipEmpsT0)R77.cfeXNp<,.TfG-3Q+a%6mXViRT7>ikIL-`fJ#*qb&u?_CAi$
YHIEt9+A$7XXi=`TDL><snVAZ-KZ->p#/";eho+]3.PE%[JRQLcaQ2)B1L?(fn1@_l8/h`#X/>kZaB(?+igB9!$g#U%q9)\jK0d%!\DPII1E+YB%fZ*l
_'&W*QPn=VO8T.q`Wd`C/1OStg5GPj5%\'hR5nmcnF##s#ZdZ5\!lnhnmLWPOYg/.XJ@G>--rf7BF)<tAAN9aiFcf^0/63F_6Pt;/i\4=A3kNg57HVuS
Bk?Ia#@D8h35UhPh20m7(MP*I@JEIp^9h!.t1]T_>K,&;>*sZ00DI;`;FHVIZMCG.f<Tu>f,C3E2M2(20'qMW>m[`/kX7<-\gtFs";4*E"7!u!HnI-I\
:CrXnN2=$WC7hT2VjPN>-/ncqs(e1C=OBQfuIiRIq]Od[O3nWm4X0`5UfH^2Mqe)%2DhPmmU+m@UW+I\"g?kuEGGG0?(R[c9?,o1=MKmu:'b';u%dnld
hC&:PC:E%[FANK#cH#@/_I>:!&/)=\B\c="2%19!$[Zl]el65mfBHS+OJM(bb*[5$&m0lZ\p2AiZ-`3@2IfRBSt^pl,N8\=/q[nfdI@HP).o0T2USWJo
#-H=)K\O@*IBaYQY*5)<QXXiqV0<g`TS`9^5\A`eL3h(@';$d4&U,IgcO]eX`!!/HMqptiKQG749Z,C;P!WW3#!!HG.'''
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

# Every function wrapped by cache_decorator; clear_caches() empties them all so
# each get_drives_info() refresh sees current sysfs / mount / diskutil state.
_CACHED_FUNCTIONS = []

def _make_hashable(item):
	if isinstance(item, typing.Mapping):
		# Sort items so that {'a':1, 'b':2} and {'b':2, 'a':1} hash the same
		return tuple(
			( _make_hashable(k), _make_hashable(v) )
			for k, v in sorted(item.items(), key=lambda item: item[0])
		)
	if isinstance(item, (list, set, tuple)):
		return tuple(_make_hashable(e) for e in item)
	# Fallback: assume item is already hashable
	return item

def cache_decorator(user_function):
	cached_func = functools.lru_cache(maxsize=None)(user_function)
	@functools.wraps(user_function)
	def wrapper(*args, **kwargs):
		# Convert all args/kwargs to hashable equivalents
		hashable_args = tuple(_make_hashable(a) for a in args)
		hashable_kwargs = {
			k: _make_hashable(v) for k, v in kwargs.items()
		}
		return cached_func(*hashable_args, **hashable_kwargs)
	# Expose cache statistics and clear method
	wrapper.cache_info = cached_func.cache_info
	wrapper.cache_clear = cached_func.cache_clear
	_CACHED_FUNCTIONS.append(wrapper)
	return wrapper

def clear_caches():
	for fn in _CACHED_FUNCTIONS:
		fn.cache_clear()

version = '1.51'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-10-10'

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
_OCTAL_ESCAPE_RE = re.compile(r'\\([0-7]{3})')
_HEX_ESCAPE_RE = re.compile(rb'\\x([0-9a-fA-F]{2})')

def debug_exc(context, exc):
	if _DEBUG_MODE:
		print(f"DEBUG [{context}]: {exc}", file=sys.stderr)
		traceback.print_exc()

def debug_msg(context, msg):
	if _DEBUG_MODE:
		print(f"DEBUG [{context}]: {msg}", file=sys.stderr)

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

@cache_decorator
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

@cache_decorator
def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	return 'Yes' if dmbytes > 0 else 'No'

@cache_decorator
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

@cache_decorator
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

@cache_decorator
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

@cache_decorator
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

def is_partition(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return False
	return os.path.exists(os.path.join(sysfs_block_path, "partition"))

@cache_decorator
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
	# Refresh every cache each call so watch mode picks up remounts, hot-swapped
	# drives, label/size/UUID changes, etc. Throughput iterators in tptDict stay live.
	clear_caches()
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
	if not output_fields:
		print("No valid output fields specified.", file=sys.stderr)
		return []
	output_list = [output_fields]
	output_fields_set = set(output_fields)
	# Filters may need data that isn't a displayed column (-F needs FSTYPE).
	collect_fields = (output_fields_set | {'FSTYPE'}) if formated_only else output_fields_set
	if 'SMART' in output_fields_set and not SMARTCTL_PATH:
		debug_msg('SMART', 'smartctl not found in PATH or ' + os.pathsep.join(SMARTCTL_FALLBACK_DIRS) + '; SMART column will be empty')
	macos_info = {}
	if IS_DARWIN and {'SIZE','FSTYPE','UUID','LABEL','MODEL','SERIAL','DISCARD'}.intersection(collect_fields):
		macos_info = get_macos_diskutil_info(timeout=timeout if timeout else 4)
	if (not IS_DARWIN) and LSBLK_FIELDS.intersection(collect_fields):
		lsblk_cmd = 'lsblk -b -n -p -o NAME,SIZE,FSTYPE,UUID,LABEL,MODEL,SERIAL -P'
		lsblk_result = multiCMD.run_command(lsblk_cmd, timeout=timeout, quiet=True, wait_for_return=False, return_object=True)
	block_devices = get_blocks()
	for stale_device in [k for k in tptDict if k not in block_devices]:
		del tptDict[stale_device]
	smart_infos = {}
	smart_status = {}
	for block_device in block_devices:
		if 'SMART' in output_fields_set and SMARTCTL_PATH:
			parent_name = get_partition_parent_name(block_device)
			if has_smart(parent_name):
				if parent_name not in smart_infos:
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
					smart_info_obj.thread.join(_remaining(deadline))
					if smart_info_obj.thread.is_alive():
						smart_status[parent_name] = 'TIMEOUT'
					else:
						# smartctl answered but gave no verdict (RAID HBA, unsupported device).
						smart_status[parent_name] = parse_smart_health(smart_info_obj.stdout) or 'UNKNOWN'
				device_properties['SMART'] = smart_status[parent_name]
			elif 'SMART' in output_fields_set and not SMARTCTL_PATH and has_smart(parent_name):
				device_properties['SMART'] = 'NO SMARTCTL'
		if device_name in tptDict:
			try:
				device_properties['READ'], device_properties['WRITE'] = next(tptDict[device_name])
				if active_only and device_properties['READ'] == 0 and device_properties['WRITE'] == 0:
					continue
				if print_bytes:
					device_properties['READ'] = str(device_properties['READ'])
					device_properties['WRITE'] = str(device_properties['WRITE'])
				else:
					device_properties['READ'] = multiCMD.format_bytes(device_properties['READ'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
					device_properties['WRITE'] = multiCMD.format_bytes(device_properties['WRITE'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
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
				if formated_only and not device_properties['FSTYPE']:
					continue
				if not show_squashfs and is_squashfs_loop(device_name, mount_entry.FSTYPE):
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
				# Match GNU df Use%: used / (used + avail for non-root), with
				# ceiling when the ratio is not exact (coreutils-style).
				fs_denom = used_bytes + avail_bytes
				if fs_denom > 0:
					pct = (used_bytes * 100) // fs_denom
					if (used_bytes * 100) % fs_denom:
						pct += 1
					device_properties['FSUSE%'] = f"{pct}%"
				else:
					device_properties['FSUSE%'] = "N/A"
				if print_bytes:
					device_properties['SIZE'] = str(size_bytes)
				else:
					device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
				output_list.append([device_properties[output_field] for output_field in output_fields])
		else:
			if formated_only and device_name not in fstype_dict:
				continue
			device_properties['FSTYPE'] = fstype_dict.get(device_name, '')
			# Best effort: fstype_dict is only filled when FSTYPE is an output column.
			if not show_squashfs and is_squashfs_loop(device_name, device_properties['FSTYPE']):
				continue
			if IS_DARWIN:
				size_bytes = size_dict.get(device_name, macos_info.get(device_name, {}).get('SIZE_BYTES', 0))
			else:
				size_bytes = size_dict.get(device_name)
				if size_bytes is None:
					size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			if print_bytes:
				device_properties['SIZE'] = str(size_bytes)
			else:
				device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
			output_list.append([device_properties[output_field] for output_field in output_fields])
	multiCMD.join_threads(timeout=_remaining(deadline))
	if filter_patterns and not match_devname_only:
		pattern = compile_filter_pattern(filter_patterns)
		filtered_output_list = [output_list[0]]  # include header
		for row in output_list[1:]:
			match = any(pattern.search(field) for field in row)
			if (match and not invert_match) or (not match and invert_match):
				filtered_output_list.append(row)
		output_list = filtered_output_list
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
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output (list of rows, header first)", action="store_true")
	parser.add_argument('-J','--json_objects', help="Produce JSON output as a list of objects with numeric SIZE/READ/WRITE (bytes) and FSUSE%% (percent)", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (positive read/write activity)", action="store_true")
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
	global _DEBUG_MODE
	_DEBUG_MODE = args.debug
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
					# A terminal is redrawn in place (one write, so no flicker); piped
					# output keeps every refresh, with the header as the boundary.
					clear = '\033[H\033[J' if sys.stdout.isatty() else ''
					table = f"{clear}{header}\n{table}"
				print(table,flush=True)
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
		return 1
	# --check: silent exit 0 when healthy, so cron only mails on problems.
	return check_status or None


if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == '--doctest':
		import doctest
		sys.argv.pop(1)
		result = doctest.testmod(optionflags=doctest.NORMALIZE_WHITESPACE)
		sys.exit(0 if result.failed == 0 else 1)
	sys.exit(main())