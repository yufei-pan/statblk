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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 52):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE('"=7F>)aNi3b6ocs6V`LdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%HJ57qq1/\
*gL=8;jBHJ\fYg4:j%to1R4$=%aO[S5W>p`gA_=$'[uT/?.1N_&PE1HaE>4:M&BCBVcr3$)%gS.F#Y0U;'G@Yf#\iaYMX8n@Cj7`rmp%aCrJu%B[E*^L
Rti_^UPg:+@X<"]%i1PI-5EaIfk%0R&0O,u5_nR:c!b6#Lh9qFL_H]p"V(AVO(8#Z#`=&H":T+BS@@i+.aple%@;KeiS0k+N>'fJWe?c+caeb2!*kP.c
!@P\`2neYOPjb?-q95[#h<*MV"P7/i+94S6qo^8\DIAEE)j?4>R-kL8ZD<i#&V]?g-@7-JM]_@gC!A&(El;iFCoP=SH"a!T*iS(le5j5o)+;WObc95=a
h_c(JN*lCg,1?)s.SE8AC(&P3Z^JraFpZH5`:;9/\r%]e(4PIlt?T:nk+e:uuEdA>ni3'/+oId8#flCHbX7#4"XTQAMCs#YZmsN))Wie"^[eKTrDqXKn
kVi+B0dsEC.H&VYe2UVJ76cYVM%'RS3tr,R%d1Lp^#GB1R3oX^+2'T'$5cs=8<*H'e6_3KmYsg8<O_.uM?E-Aepg]cP,bECjHqsZH0e1Cd\9rD5U>r:9
m,tSh"r(Ck161U'T,5]N/uMUoVB<`&oP4aUGmn-YW_#nriQ.^#qG5N;l5qrF"c-)ripNTXm"J?*-q+a0.X2ELo?WSQ0#P8;,sn)rAdQr%)F\(Wm6*J.'
iV[PC><JYufF(HK;/nKNG%[Vm(iG1]$H\::]s`Eg6+-h3,.eoh$)kEP;*s'uoVY&GnA-YYN9**S4A#hs5ApKDV^r1\C6BejDr=VWYkk:4nS,:C`_XF6$
E0qTu>9qa*Nr1tb=66$7h>4>1T="cra$StOB;PS$JY3UL+<k9tmR1Cu6^C_;bfkae+qm9-tFkE'7S4EbGPg6qL_"RNrp4EurZ1Y0eYE+K83R`iUn++Ni
Bp7ldp--`l,lt.PJ02s='"UJ4,.>4M\m$mMqF+X!m0L/V&R#<$87,4.^*74t%r_P(-O@;G(:sRa;!pPms;Dg)%N]FHj]_rO$has&>\qm.G/ep.Ym'5t\
5lKX8PqWc<L.Qf6$tM1<q1Tl]@[oOqgTk$@YP6smOrC<"97Y(FcLr;pAO0Sg0hZC#2:t)9G_X)q@;-`&nkJ:@7=t*0@\;u_X\VH<l6+]Qo6"*:NTIDhg
f/nnh/29Um<,s/[M5gU?)OKGdb^ItGJ>?!\Z04lhbgbmXbj0?"RTHH$DAOe0RY*OaY*IH2^iETWY\:s9PDA`eHW))g#aRuRcKXf72R'J='l[84_%f+/P
X)-'n='H'M9M;E#4!Gm8%8k@F?F4TV*:GAU&#pNALGO5fuR5M8+l,dgF5qI?_&#*^pE<^\PW`KUSm=TcNbG=YB8$.</uDeV70r[P&;j5S].BC[ad3_?)
UCf?ld`%4Lec"4CdLR:<8R-nuF4oF9/liD@Yi,9c5AQ(?rCOY"d8`>XA;*V;mXSY?QPVX@)'#obXT"sN7Y<gMMD>6bt'd[IN!8EmD67p:4,iu2FU)rPG
pp(6BE82cGZmD^Bd;jll<-$hB'hmOXV#I,A(j\F#P2#Drs68o%rj9%kJ_6="B,!iA1:cR_-pe/N:@+Oa1Klq$72A_=9+pddZ#<0`c0A^8_OLbp4/C%nW
7.km4)H0=ncqkSt5EC`f0ehGg3lD@%IU`V3?ZqPe^Z%$X1>Po_0aq-Lc5k#3["3#K]"9H#DM7Os'nk0Jd[<@J.F_B2WWmS"e!e!#;)*4f!=\8CJML(Cb
+q1Xs"*s3P_k`VK(NPB&]@jBQ79TlDa9'%H,ju4c.OdN#tYN/.5>:35Vu9-^C!:g_glqHe<!R^@fXcMhXQr(!KXMA6:pi6F:%Yqr8=U;=`SRQ-5)CfXC
<,a4TikmJ:.49!]+"[/@88AT@*lHU[LOn+KfC.O4cHf'5X(iGHm'1X1*N!2)Por@&[)K157Y:oLt3g&`I/GHo[bIW8Gm*huZa*P7F:e@:P//Vb([.4O_
Z%'%H';bn)ZQo@r=?6n?O'5*M9+4+RYhfOMWq9,Uo/rk>tE."R3aUIIG.@oP\(Pt7U6h9^<Fp:%[0=`S>q\7SVniYT=--^%X5-h$c$bfb<fm+>OA;fk-
H/Xi$U4NZ_1*%dLJ*H577*gZT.OE*RM"m7n7`*g&uOK!QP-W3"ac]>iKDNJRak/u3S46IHe1e*Bb'aPd<s/oh2gbue0&hR]sFdU8eUXR.;m+`N^r7HVP
hlh#L[C/\K,honJ8R+hacO]PRp63&^j5N3-e>OC.KP)K1b$i\HUL@mP=Z>na%ASSJAr1"=?Iq%mY8dQ1^Vu=`aIsF"n5*2gjA/ZL2Fd=E@KUoe?ADquS
;ojP0"jL3=`D_DIu*^C!LSMD0c>LlG6OEd)s4VjCRH[H(e`ehWMNS"E/]cp4CQ1'_[9K[kWLP>K152N3H:f`=^X5;A\PkqTVAZN[4-"!>r^pGp3N,RN!
<5K6o2<ghIW:22DJ"A'%?bE0T?H1)nHb">3Y;Q;?YiOTjKT]b/nTo`f_oY-iO-O`Cm`.$/!jR>mCMh>9=;%:&prd2$HEJ?,Bo^&%4k4(lg#,@%`M0Lb/
(&D:D`JA+,6X08])d[ppG0+5InU,]4Eh""f)n7g`pdbWl$LmS;8Yf^me"UnP2TB'?-Hb9"!h?6?[W0-D'T/Ue8`q3b+0["*V7]eJ?VXk_JLC8qNKD>BE
&\jIOR9Pm+pZ;!]::'/-j8Br2M]4eCqgP;<J\q0sN7q?lC'RI(?n#KiC)?AF?\ROU(o-Ib'jZ)\>,.rH7SCk#=5V6Lf6BpY;-EgR=>l\A^rMV]?qNYWa
CY:D;K]u7L@N_2jDLL=.lV+)&;;$"7e9M+`q?]T1a!M?hB(O8he\%p1!-lCj]k]+AksM`6EK=<+MkQ:$+X\#5pDS-UZMNK+nieGq7?kH;ZS=qXb>#'07
pAQ#,a[Gl(h\\@07,(]\)q14T=J?FJ0&q1`WD'6k)EC6'Rj<<,aZTQ8GIacE$6\;@>M98HZ:t*.72p>`6,8g^C=<fIB6+"RBgMocsE0@_X[E7q,4BmeF
s?<WOZc?L:E:0'+L?p\hpM#a`LXEq@RS[fY\6A_tJt_6\p/aCf-kZ:u48U1Fo+e#JLOQ`mcFPeBGu")I[0ASDSaFa$R&a9\%<c.iW%=qDd<H932M,l-[
L<I@/AT#I+%5aC55`9(6XY5N;?$3FG]05+"(<c#5[$igq]PmD)eX";U-c,\n=CPJan5&XIT7*\NT_^_U>'ED:8.Ca%(8Bh7;oL^(a8M*,\qH9A'De-pb
`4"2E)."?/17n[Vo$/1?Yd]c'mn"_2N<9iAIcU>%e)m(^rfm*;8OO\9T]CLi3K<'^_f?*2!n82WSB0b&&]k;bGL+rUt\0,dH%o>aG/HeKWm=[X4dS\3n
&bjr`G=2H/:ktr1kIZ^s.eJVsVj98cmoA`':\>Z$YmrY!\Un7^)cZEo))"ERVAc[TTukiSQqA$b\Mbnjl:l]#:EP6Vdc$,!Y&(bU^&J-/no0FNmK90`i
JI'li<@_tWTrd+^Af5&\=SRC"(1FjD`VB1(8Is]F/$,b_0_F-iW)\9;PmB6r5.93VH96^m19oU5q>%[IK1R2%ibN<`%e.al\,E!2E(@5<MC^ZEDhS=%b
Rl.G,As)H5&mK#C]B@BGN$7-Qd3+4:JqcA"jLs+g=H7/f-T?F;";rM^Cqs\V<J5p`+54N?MQC?A8@+10HDoeZ-jr-d'a/@L+pPgb&`>?/F2:MjBHZ/->
i1i(<`,XfLq,%aH#J=X@_G,JDt!'0_5;)g7H/OjDhF(8_"-U*EPG=$;]\D_W"O^;F8BYX4<9OqpZ[J8(YP>!W$Y*jEmN_*9?fDA'$:9r-sQ6O>fQ0DXU
])tjZpIa4Gh4Rr+NDlZ&@Ub\_qe8K)mcBANu'M+(2Y>aCurGQNX:iJ@p+>U5:GA,/K@<M.?JK$'?$f!BbS>plZZW&#N1gq`JCID"X*?c_c_D"`;##Rj$
GNZ7=O#.0&[Fl>Q)C%NW_iU[WBVL]"X'CR_l/j=tGoju62UtgYhS2);6Md?for#U2YZ'5KqO(H+\Qo(o_Q$Q,bN3.iE15a:,MeB^.^Y,WAr/]a^89TTV
.6ifPbQm63G_/S5&,;rq&%';qU18OW)(MgKUiQhWUj32Q?KS!da9YeaWHh!A.,R'L[)=K;oiJ,o>F2Cono`,K$nb!B(tfh@DRN)`$j%&VQb65k'#:5X"
:O"]Tpsc<c"krP)--nd+NU_"@DRQ4NdVOYCHotWU2rW5+Xh0;LKt`)TAfEBQGpE<2>#8jln!]"\>_t`DAtOd*'lbfn0D9qPX8QIh+_m&em/XfA80U@+i
:TbipVh=EK>H'Sb8VIt'Q#*oVZ$p#e"%Or`;,d>;uO62bbW*c5,ObNd@!BS@PQ<Qj0KO;$FZT2-FMp$X3F4uZA25Ji9%7Y\hLId.f<6KC8od4*pd3q*2
$K[4?DqHFb7%^Idd."6/OB1V,)CoZ)0aRC-6J[5b8h41:;f)<9t0f3P,]?gP25>MRkVt=)c=ffmhF\=Nb8:=a`==s5O>E%";h,.s#2@X=)(Q?Fp_9:6Z
fL70>gZDdbO(L_J/pr'P>bnb21L[5Q\5C+N\_3'c2+?Yn%:RJF&+G"XPBY<0`>]EDC27GJ'_%)!O3b=-\95UCX8s21n<<%KEKJ9aO-)5n!nGo'AdiB`H
i[PG"(9ooD8SgqCs`NUd<H;E?\D%RcY6McMcn`7:H]mSgqhm,Aj2B&fh=`=Wt=[M8es$Zc4h:uqucM`J:E%Cs,D(OEN;>;aG9eRemCM$JRnWPR,kZf\?
SaQW%BQhKXN`Fb/8[0i^KV*a)aY_al5d8e%)LR#@gib?">8$!-%hcHm`RUctI+9Ed6-1gG1kq"E:pgd8R/e@EO84IT3(\WTdFdjl6!C;a_pQ&dUjWT@&
D(S@7!WO'%s,7Z!/hm1K'`S8'?t>q[,BL[N_%].__\<3#-Ms09M.Gs.k;DIrLga9U%$NR2!=LR&-W<euOYSer/%;+:uoI>d(YB*;rt<.22&T=N0=P(T,
Zh?;B%[j(4EomYKC(@@Y"XrQc-A>)c[m&"0M1WPjedg:knZ_a37aod@Vhi>7ZPdK"*hpGlViU8eQ:B'Y]::*k?[l#[K(S-N4V;6^'_@OnRId?F?h5etn
WuWT]4n-j7-@Kf!ghiqTAnm5_pg=HEQtVr7+*I9:++B?>jLof*,3oYb,lo!d:'_mAl%R&n@3r@-Q6%B6eY<kIC,oEn4ju"!U@$]]nYPS-n/HObW!V1UN
Q)(e>k`UA])iCtapnJAJ#94Eo._cX//%bHCZ/>[14CfNM-?8#ZK6#0-R1j7WVN;3Mj"Md=8T:;f&ns%0o(K4_E@i3GFg,lS:%G9VCgf.l10Ko4^IYV5K
RWI1e3[k$KPq2>Mg.c%TIT[4h7&bJ<O<kHOp!/UQ'"jqjK;gg_R.uKX/;q_36b,]*(lZcLhS$l)(fu/sJICJIo%t^%*Z@#Lil+*45)!XeQ:KQn4KCT,9
3l1#(jcKa9(DRa-%t`IJ$ad,cOLkY[I$WdD8-HqA@?&Y:["ToBp"O#2?DpsG3*j*473;4*1d*'ggVJ=],C7[5OBQ*P>]FSHfFoLCbrEp"<GDeMOTS6?O
P4<JcDccgtb5_n?X8;Aa8n]>C!SD%3KDN0dPF(LE*TRe?lSI!a11Rc.<Ag;R?SSNDS2pDNq&*h!.D(A6A1!NEFO%/tjcPUNfV!lsdSc@>7`cHJNN6K-/
:o3I/BM,;:!<5.o?+dQeodm+sAO4[DQeYgY0o\Yh?BUoWTgQ5FU-t_%mb=cBdhEh>J6UDR04,dB4]HQ?i)thM,`F=!4;o-miSq50^#(@@/tTaL''*nOi
KRZ-F/oDjMF1&oDeY!M`nQNMoAFE3*pNYUdC_GKB]>BHA2<N&Q%P+s\JWqmjGd#*,?h"4rWL68N%Vlor%2T%M]#u!YA>W&m@A=EPhc9>Ijcm>/RL9[Kf
/oiP05BcL#[B.fPCB2I0VTSYos<pC?WT'@ar<\WY1&g>>K!:_F54QeVD3s)?k@eNJN;NW?uc.iVY5*PWj[[2d5H`)8Ln:[[Ip7e\=:Ak0ItNTr_-K-eO
p/**(SY)s7[?K92A#^$+iJl3j!58fO`IGm%p)k]JP4`kAYK!LER%ms)Y'/L22:3N[3aD*_01oe/`IfJgY)Lquimmn;;Bq!$QSS;^l/];GoD9D9;%i3B>
9ioGV_J.5fW&T:Z3??"!'F)"m4djLFE`7./_XK^,M?6(b1Yf7"0%MP%**0^YHlK("\qUUtf(>D'=.)q+$E6QXQUa%U3&uHIYe;tOGCtNTnG^,mWU];R`
_QueVf<1JM.V":<-$)]9'k$[s<>A(;L1T%>"qi"na"[R*[]jfuh5s5HnBsAU>5WfUo,<?iW[RDSY6#j5%I5I8qnlf'gVsR?8=WjaGrp%G6.$Z%aW'Dh9
W7E!6MPj%I1/ZR\(gD]fT2d,a+`'gQlrtP?f/+tqljuO>^qPk&RVP"d3mGV'+4tcj+]U4Qh&r\7BT_!Btnac2ZTA9IM$/TPFmnQf->s%$u"L4\EOR7I&
Rn"<!`6dOb:fX9hf_mN:=@(CnL;>%UfC1RThCS<ODlcP&QP/UMl^-dAH>/n\p+%VMS"9i?Abl(,j`okHJT4*;^qM_KmqRl@a"%jtZDMqAMUbMk-,F;22
<XadbeYclmrWb[Zne&L@Wd&f#$sI7Bp2i8tsnSA[+@gS2qR7hbES2"rFb=&nu(dK.!7[JS*E7TUm.F=bc*oK9?%aO-&s.(,n(;e8e6Fo(BCkm9qhD@7s
?]K"k!N?nH^KNIAfJ*h:#QK"DLorW@sf:fe7isgqLGf*()24;oB=.s9hc=H5"'Yq5<(PV_CV1!Dc!5h`gDP)G2ebfTQ(m?FeQ9!8dmg"G0Y3f%(n@\QL
7J,q0U.5KZ/2D&F6b5RoL;#%W2T[-WLi9Poc>U.,(ARIu9@570`?+71$W;r4Zai-B'tUskXL7*!Xf<#b/jcmq%eR+750_1Iq$)n@&lM!PT..'Xi^f&pJ
`.53ht&aNSe(tWIdO2GX@LW>?*)'OQi`32BM<WhQN`@r@)u@`!Mmi+PPK_p+P6hjA49pRk@Qrol6*k7lU[]s7Fqm9c\N'3#RE6Y3%G:YqR@1<_<,^k]K
R:?WGreJocF#<V609GGP5hS)un+T@rWGU!@):BANl7W6RglN:_+pPj>%pRW=#]`<N'<Vm<H]TT;>RO=0.3#/d?ngm[,XRR^pkR#,k8)SHWp/]oV,&F!M
^aE5,8U\pU''(G>VYq;@Uj4!W-0)Ts+lRZP*4\?i./`9?]u[mU$;3hR@&*F@$XC_a[RQ_)U!CYFhTp_ENHgLED2'la3T4Tt'<>$*e4fQ54%qat#HlRm%
!>pC(8j\G(9c-Q?$@"EN\@ZJ`Y3]i"SEH"As/9@7?>IY?/Mp@F*>k^mq%tVlqm3Xb4Q^jE4bi!FGY9BNZoR]C$^E>&\M=_P,>4$2eCH.L[fXTaePJ\%M
pmo1m*Q=fZ7cct?1mD>CE6X#(7/DZ/#Z._q`lJ#'R=57aN/'1G#mh>.YUA:3KODkd'jhU@2oePbes44;G"<GCC.'51JYO0h*QY_>"=Aj0,=ZQr1]r)[r
>(:*$Dk*Sb&UNeXTWI^;SP<mOa'Q^:Q+8"l2)e(*c5iX$Uh8Wh*,Ua=]R*\i@3(J/6p29B!HZ-RWorMC:'XDRDF&$lUc@2>%Ya!a"lp'$.58JK9HW-K:
3Q6V(Y'gE"4,fM3\a\8@$tI3(l0(i`Oge:6Fq6>eU0d/",#)D\0[DXO*;ps!ZIForshUmBL*cLmpOm34l82`ga(e<]B5-p;6=1!eRh4IRm:_]Kk;PT'-
M9kZn"<Eq1"\1p$ZdEFcHHL[L=$6AS`OU0`=<Z^RuYY2Ftp.;u%i'Qc^;W$QncH=).g`e;-/1('@7hSW?Ap(,Vh11q)_&htodf)<cqGJ"1FIU3W%_^TY
&RD:*lnUol]0K1$X<T>u^J`Hbr-T@$.,trP\atk<#SRjbUL`R3eZ6bL`RPNBd_35N]8nJbr?0UtVVr6qo*l?gX[RPGu0%i+nr9g0IJgAaP_gsLS,iD+V
g;oHLk[d]1<ae2rmJq]"@KGilIn^(L-$5X4K%:f3eHqq)b3%0nR>&)p3A2"91/0iM"n9/mO^:u,`7*5oh]FqQX<<(C`eXqLVW3E,j4YrSGkkiIJB(=%2
qXsX/kpUjG/-$2U(.X:K57Z[.d!d/8M#kZr0OE)Ro\8jq7hB@CW)V*mGh*"7srX@Jm`:hQ"<VF^]A3.r#H&hIkgTh7&>5OW3!1O&OgW1Htf31Vho?>Q$
P@>ZAW"T%0.$Or)69;"XsL)#RNp%LTJG)U(R)9h=bCZ7V'fOJ#2->HcI20X6K27C(7sF/[5CRdCG^S<Gi:fh7WZq!FA38FB.o/So^HT=Rk+!</4,g5d-
*aAb]j0%([o\dtM^TrErPHppUpc^;kjg<oA$>BD"KRF8LfZ^>V('.f\4NDlg9&a>\77I`#4`ZNJFjl?\(gQ@ehUKY%#>)rXW)nE4EGpj2pnXfqo@=@9%
Y&E6k6-I/HbJf1Nc%Q/`,l^?A(g+^8*k8)"/HdZM]9'M+O<g10'$sUk4mm?T6r5WUZVpXIjF+-MORM5sn(k-Es90:Xc109Z-WtN-^Vs&:C6\J?]:mMTp
<ZH@P/7QN<PW*"4*QS?c;iWAof'qjrb65_\U2;SdoFn3NmQ]>;?a!*'p!7%3FlZ-=lBF[hqZqL9.-NNMR>n_ph*LU9DWMRKQYA5D5h2?JB+nY71+s3gq
,quY-Vu#/lasQ;U=PV*FLa=AOSQAD@DaaLn#:4j=7lIa9jdFNq'#cSZ:s=XB3ch_!thVG)m<2cO3efuqt`go5%F3Pq3f&2b4k%,]#9;\C,_$hYS<'oZ0
:Bh[G+G[A]:=WbRGe=.'9C/-Rm]H%]\FQ0EcC&,OA$a+pMA9LJhrrVa]Z7k_qOON#9$(%QI3Nn%6/u7%Srhnm@d$W=O.]TGmOUI5[-95N475ld!F`S;'
nHO2:&MJ#c^'0>`W-(;UNee=9c[;Z#))_0l"P&CAh_@)m]mZp5t!QU7!b4-QB]6;<u=i"\K.E9sfZ>>E#(Z=#5?ko\RtA<Kh&R&57N6SUsV_98Z4RmpU
3qL8:HXm!LsSX^TmD*Fj\p9a/r'.CY'J9Zi`Rk&D/ZImjp6g.m4pH1TbbW[3`)B4KedbSXl1s3J%-[XP^A7oNbO7P9^NtENFm+ASrl170L2`gN5_Zl^E
Uq*ejE(=m!hs'A49J-!"@#18c$cKU_Udn\7b4n3TjT",1LFQMAI66Re=?Ol"%n:dY7q=S;I;%.B'MElGWH2=N6j/P7L`n:sps$qZ"j9\9A:uBqK<eiG,
PHCIZh8'af"]b%.u")h>.A5t+Z]se.sFK\_#LF\_8gWjGu/eU$DX\a*6&rn&aCZdaTk<H\r#Ut^7`;J@]3s62\qF]YX"n+$[2pFS29JFn,$dr>U=kZh7
0'>'P^Y,l/>8*0@;Oq-lX?)L$i3MkIEdsfReuN["'o-"[_4M_M)WGi52)ZalHb,D[)$;VqsC_'_:$:H`?K,-CITDq:7.gHM;mAHUk?OF4_o"f8+/koqX
k'iGl:?+8t=DSgdg>F[b2E4gA/Zbo=YE=Lorsfi,LnmorG/$bKqg^'*.!jYml"J'-:DjS;>]l-!+W=]IKP<i#na(LM4Hp.0.J4-$37d)26X,-3p6["k$
dm^8o`k;&'aED?A[=:+[ZGW6mI4OI?R'Kg+cQ%h/6bl=/m4A,B8eo?k]^;sn;>5>2J,3WlO-S&NW&=OD*1aNJTh0r=W@bE-#S=<ETr/4*OL=(d)AH3i'
dEiaVq2W_j24qJ<C42J?9ddWhB3H\R)kf]*iPgR"g'[?Ba\\H^q*^Qk(rX5Q6PtK54)?Sa]P$j>Wq'=K)_;4V58\H1EV@D!4Ie"T[BFJ'Xs?FPc_\oqE
4aWM1S6@iHC[C>P[amR[JJpL7I&:$rK#"4,t0-k3<LK_\#QN#gLF?O-$ui9psJ$4&JW31f75;e2ZMJtQg_??WHL:5CZ&t*)W&-Q:13NcC;ogWiD-Q0fD
?',mpHPc,,?c"Q^2U)o4ib9kEkJ5E*GoUs-m``ii@NS3R/[QMd&]o`$t!@#k(dMF?t/C8)`H2U]es;B9t\_cb;X(4u;nV_+PO\T*$cBE$R.SF-NTplKs
0cL6:K`hnjK9eAuJ@ppf<6P>\DKQ&Fe#\jhKuVoQ$jDt;gPW*!FSSSONHAeMkeD3JjuDi+adm$Z\21G\hD9mFY,o]cg"3U5@<AYJk]i1HRq&g:K6(UQb
Y\PqslGii9`3\aT>IN,M`:4!LTZuU=n*/5;+b>lE,"po'(qH*?4[?,W6WAVu#H^%oar5=2*U",o0a)Xe&6CNVlp^$;ul\NGND`uqTL9(.<>@@)jqps&$
G.G*&\uNMLX<*jKkgnRpV_?-d.gqij*2*15hf1((qVcEU8$LGn.KDiXTX&?k'gtdLQ&YH@BbN[B*q*J)YC2W4R7M@%"?I*gCP%[<i+%Bb83c<or08[8O
oj[O(3-R$FYuXgk'?Mt2KP]'E)FL^bf[PR3+%sYdYmc=K[ZPU>UYMLqqSk98'-!RCMdZU!W<g5r9390>po/&/o:3%lU,SmR^!A.L4s[$;"XIF^k-<o4(
NA5XY+U=^LIULLTe^C#<,m9D%0F]"_A<k%Eu+48<Rs@N(\_?hpuF$nG5*QQh*AaF=N2cBO4AF461sG[7MA4CU6+A$,i[iI'W(t\=7jW.![h4kH>HY#g-
C+\K^9_BXd[[!gK<PcMg&"__$Cg9jmJ1Gf=HDHSn-R<g-`("Zh!6k6T19gN0#h.(gkXj8t%d6bQ_G=.8ppVDE;tGo3M8,n0`M*@L=Bcrn+iW]0Y8<Dqf
BIP0-qSDu+JHV7:OH3,;j@N6hD=0_9[fmlUVUq=8&s33+WRJ)l"=Ro>lD&-KdRknuqk"Xu[WCL=@WSM0)Q9%bM=6Nt;PeiF81m9^^!I"nC*UJ:B"I)Mk
MV8Fl`cdS_nIc\,+7hbBa>TS]-Z?6".;!Y7`+@+#K?/arOFB68WE.oMc_LiEe0l,TV*49K&b=[n\7AZK+pmhX<5u2NK76kIiRO;]WRXMnEQXOGqL^ot1
Zm&(n/ru)b_l8rBc8DsTZi=983O18'4c[n[hj(C7"0K-[#_?#<WM<fl^FX/SI^qjRCY)h?9G!85=SB"3V$[$B0<l/!DE)N1r@R&q"W^!gd`kcd>XQ==D
!8=E%goS5-upf$U+W5>Z0]=D&a1g_O7V6Nk*FfmhDFGlI+Un$9g1C<+QH$83%,R=Ej^9\ib-!8ETg'`W1C2mE6crruX6A5jk2^Jo:uBmB/dA1^KQ8E>C
6;Wr/F;R<qhf#-t0hJ)%3YFVgo52k#UGpqSp7d_'7A"lc3&\en.m1(u>W+56Kp\41:rI(aIM;H9:I<;WnO7WJ18s"6@IQ[<<_/Q9Fs@7jp"Q6@eAhXrg
s"R8>Yn0?Na*We=ok)u,`),)P]c/4<e5h6BgQ(lDb#=5,r?WbZ`jg&71GHPso?=H).jeClmACA2-j!&*Ag]1s"0(+Pp>M"^Od/<q"bff'1AFiQ=[NH&V
rjV;J+SUai)oB=[rlVd5T":5ZXWV$*;JD>X.K!\NW)Y'o(hdKY8E[b2\0m)G,4C@cLB[DJ>'&L;q*gVHC>Z1gX@aC:"W]"(&jQ)qRsMQY_9Gal?drA.k
Q(Y,V%6'M_Yku=)EX^$Jq/R14s$4Hq)]mo&t5<B0_fA)l[`T1a"L='RlYsdH-eFCMJ72gYSg'lBmt?<5]er.asTj,D\0jdA0lp3CuR=77706cS-]qp[k
5]6\jgCUnWo];COS;Y%0.Pa$B2\^Ug]7[(99Q<S&rg`]pF<iDQE"8*2FO;)V^]*9`73*d*f1K.fpo%4RiPs4(H"l\HHsEO]kYd?/4n4YR(5$+ROQZkh:
7/9N.9:k"aUN.r6`:]VsEQTkpmAqrIROm[9T8e/jUhVZT7t@>u=+<>9/dhi/1;d2[sWnW$XNhe?VIX'ItV?\\5klarb*!isOZg#J-p7+%#<B5"<dgT7&
M1ms]K0e26![^IogK\oC&\BT(d4%AN_KT"MUjo2lOB*hg?,_IbIgD'm.38qg$"!7<8,ta/U;pV7/2GU+lN>[*2M1?K3\SO<FFc;JRWgK#<>1tnTmDdNJ
pnC@6#qjCuG1uH33L1<%ip*"/.)""L!N!q;Hild/k2@<ECVWWB,DK\mk^r"u1*MqAjF:lgE>;WmF[-Df4$mVQOt)./#eFY^WM&O!G#^L/7.N12g+0nG=
c.)HUI!I1@NQ5NUe+Mm\7TVM7TqAHo)(*kG%()X%ppEfnRh.:Jk%s'qTrh/(:d(Xp[f)>idXN&7cgZ0Lo=,.PrCHlP\.dgh))SW91N81?,#KeS*-6,f&
-\>]/.!`UHNAuhZ'a[:;*hj7<^@le-V$"<R4LY#%\l+_6I-jMp!AS]\0,FG4k/5O0<7qq09O6s$t6$%=I.hFFT@a`BBdX9Up.K+F6ApMs+qe_0d-mb7)
@J.Ir8+.W8LIYMq"o%Xt;LL'?0JZa`?=5egY6\V,E+R5,<Fg6`E6Adc#f4fR1rFq\)?a;#*F@7j&Cg#g[;48q>+a:0D9Xs/*ujh_B1-sd?eK"gVM6eAZ
9"@K*'=1?mQ_jHQIRk6_Jhf:/Lg36O42e8DEI(lpUd6_cs:XV7e(G\QW,$Q/KZuZR2CDo\4)OU5!nCA6kB'lRd^2a1T[Qp`3TM]8<hgHb);ieI>.9J<.
Hg'lLqZft7=KAJWDlK?eV$U`a'JdUK&if(1:In"cNm/CX^5b_;X?I^@3F<FZj!aB^CG5uLA8UkX\.+5ir83.:%#(KTXL215"&)GLJu!*EbcD+'fI2M8X
jRJcIXnfbe%(NKFS(u.HosGk"$QRf.9rXGFW+FWp8r@B5:sHO2NPnR>IY&'UZ`KBZR0:t%\]CU_.N$rPf!^&3"\<BNqV*ID^\'jJIkPVC5%t$rFKrt1e
We1g\aOi.phiUk,>.!0>Tb3;3k>7"=u16^lkUk<[C8V$<Od.bYG'CS7"kM]CH7PCm#V2*t!2f&>O:SJs<=fRrk.tqJb8R\IoZmS;qW:@:4:3WQ8c2+I;
i?g!!Q'7Ptt'?n[!ns8NZ6R5:3AkQ:mu6Y[mR?qUC/Oh@Nf`m]6u;6Tm[2)bqiFH4MoY0QnGJfHOp\lJgQ#gr=VAGI2Yp(fTUKE5FTc@lIq96s8)R6Su
ZK;.fXXH!I%4n1-j:fgrn%KgseR6p\m%%DH[MM,l9@-:,dF:biJ/p3OPoqLbVU2(o:</YXBoBcXhH)\bj81!_&kKYJ2cOt0]IhK0D&%=,/YrPq19F9&m
$b%nG$Ucl#*]$K1N2n2bCBl"dYD?$?D#dK5VG%MpOR+2a-+_lVXmY1K!t6h'E;4u&Wn?Z4StA2*"?X`/oAZ0d.$NjGFIM!00CD#$WAefl*m[6%B>-$TI
6g`'W.QFBI#2&r%c\;ZjuPnrUa0p@@$mM6+h<cL$42KIXfsP-(W6%G&SV'G1/\GY^`e:bjO'\%huQ7'bQ#b7S'csjoTl,RlXrc(f[)Bb@)PZJ\IM1Nca
,NkAYf?1E3,ck3hW<k=0!n']CL'>klDW%$&@]=QOnR`[<<oI*/43mj<Rde&(e<,_@^E\Ri!;+TZGkc,X%eZVEI)+U*AegQ^3E78&%*ZAk,aAb&FOpJSh
<T7(P4u"7C"!:c]bXU#h=5WR[%.%:FP22*uhF]ge431:r(uL2@Y2ctItN!A0;pbpQ3fQ'I[b[!Ib""$C&bNJu*B^OM/X,;`<M'o69S04n:Co)i#P?q@p
2NtqLY0KdhL/E+T:$VOr@B"Z.kc83R.-DE"qXc&(A?q_\e.A6RJ/?anYp"9:W`7XKr:`SFQCQ.bMB`5"9kQ.TsOfLOeP4JfJ\N\r8J88S!7dB9`C4_=1
KNH>Z.TnNUp8.DRP3$2>LqZIiD7ZPf!@LVF.[@qSD%s[VM5r%.f5)cq[QUG6'\4:'(=o1s0*tIr`F9QJn9<si->h_]i/;f3Ka+E#g=rhh?MU4mR-qJ7Q
c&Yo)`'0;OmC-@AV"\m7]GV7)hli)W*+\[/Ku,Z.@jZS$)J[bNI(HpC6uH<-J\b^<-1fJ`9m0::dUFZp'C=>46W^E>75g#CORi#>q_ElUg&A1$iWp7O1
\@]15n]q=G-&rZFo9sO77j]s1=6q/ts=k])^jh;KhpTa,bVBCRqd"7m:^Af*jc;mLktWN8s(sphOdsQ8<TqB8fpf(CD%#$IKmPe&@X/qW/5?.AP5-S_I
>SEaOJ.`OGu_Ir`jH@=\^I*[(s1eF*SsQ9k*D?Cq4fFe1/X.#X+KSfF24#HT>b"*UbZ;)=Tq?:GuW@c$m*KW3)5NoE#9DlL>+[FiE8*&#3o:7-4Yk\Z.
D#)p.p[&q>`h;YBZe%7d1)AMEJQ`TIsR;NePLSQTa\,j&j`h\,UUf"J.d%g,u8:L?/`Ucc*:1%D]E&!Y(6Ef8KZ`i[W2;^.Hl+jWR&uhOE#r+C"D)K8b
P?UF!+73GQ'+==3",U!3fl_C6>^E95a(?D$!MuKp(Eok_1mNW9O)%I:OaTte+tfn8JXn+,a_VAt5rlTdIj]g@JOV,iLUK>+$r@[0:HU>hF85@L@M5Egg
D"^>BS!2+/'<(%aqlrcctk2X(DX5F$sZnaUh*R5>bB*TXTm`3e5qS*+.o)QrUN1):ePKqp/l-I\1#!SX!/I:;Ql+2R>=3db!mHT^@_76n)"g!KP+at3E
=:$_H"<TB'[U7@`c2QY,h1e=I.%DBj]^FA]U!6.G!%l4<H/dM?L+IQ`e%)(?LZ7DgI<b!-s4.^HTP6E^fog/uA:Q>OTsW6(o6R^!p*L!u]#G.4<)!(hY
W.Ke*^<I^u;`!5;/(+VJW\if8G4Eo29>Pt1ILj_jgPUP3$A#IQWgiX&A^Jl<1-R^A1Yo4I?-a]uK%eZS$Z%]Zs(n-kAJZ2p$W_I1>sGJI#$6OlX:C,L#
*1^VbhBQbb,QYn[Or27T9'm@Dk)[SWN(=%+`Z;/=;i_C/uTE6Y.EWX3W&_G%smA";)o;4:pW!5gNRLIHbUj5oEYum4_*Wk-Vd0PVnq&sqkGFWl?cD(*7
N#H-DN]i:r&b`Hr/$A^he>OH"4QKf(0P_t+o!.89H!Zj.mqi*[p-$50R1QBuHD26<eLVJFbA4*>_rLV?E<FK_[5Y!K*>8Palr;5j^a>OXWWMGJ4=hsX[
,G"jol8K$-hiFOXpm2'VOom.Xr.\DmI6Up`qLT'1m21&S""Lf$71t5.;'PeZC#GMH/+PF=;8%`<*ca2g.(FJIhj?l6pJCIEX.*eo@s/PSCZ1"na+-=p=
DsLqct!n7!^9_7u<r4)>:1+`6S=h#%&\A/6ckKk=kX&c&-i'mAeT%XmTkS1OQSiW9F5=qDs:u<IT\Y_QNAc<[9n5ktjdIdH3QC5<a`[-2-g[5f"GBD*c
!u+TDPFGnS!4S6bkcTO;?La;\?pWZ50\+<'C;+,E;E#2#>[[=R^BJ+/Kd)j)16RF2-^Y4@@<0i`-KK[=o9?A7=2K+'_9IY'A_Qmf@Xg9b,HM-)kuWsFZ
iR.$C%A`_uaMa.L>f:Lt2DMMMtrLQ&?h/]Cdil0fU*ETJS8DRp5oDjrqES72_p'[LJ238C'\G*0/>G*7WMGu$h%,f-#S)%@Kp>.h6Z;b'lhe*TGj7RQX
;O#r3'4`!G3)b[F&Fi1H-etL=q[Ll=CeeN^/t'D@jGC9/UF%(gBTmOFHau^O4i?B1[Sgs\ANpcoJ@u0.b]-=Y65KoBjV856/r=-X$c*T%"akgG:^_1$"
,,chkplLVqo7j#5Yh1jPWc:W'hMD6N>g7IbYUK,!r]V@a0($"BOP\..WH%^FC>cIN<,J&(3ee/pU.=?Wd'e5fdAuAN+OKdI2s%M+@p%<2.PS@<U@\Q)W
rgc?dni?(KhPsQ;$a6HhSK$Mo$nA`5gP/5<7c1@kOhZ/jW;0I(srX-PN`2I<@&/<EGPW.F56??b'IFN<bVV#U.o<J;r<#!QDDJ>nS?H/i[PHX+8QpctT
Yc[f,=CI<]7Fo-..a-<r>a$=6J$fV.dA-%unO8*G&[PX*P=`!_$q43b.PC@1#Io68Q'^8F8%k%#:0EI=@r-Q\2D&`<JM<i!K`,i/Di'_Wg`,>!iH1DJH
+'Lb/:"AGgTGL@kD`Ql"1)LpUZMu<DVW;ibi0ZUonKl3cH$>7tj_I=`P`cQtK6ND))8fF<lAU_P(D??nI[2)6,5]!3Qk:fCI-`1sJpLR&r3K*[/ae9"T
Cql7ofSN&EY,a7;Pod&_QoHf>;L,lrB0^"\L<(Yt8%$UO82_bkgsAou^D@F]NFXH$Vi6:E!!2FtZ0DAj''Y@jZ,C;P!WW3#!!HG.'''
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

version = '1.52'
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
	# Refresh every cache each call so watch mode picks up remounts, hot-swapped
	# drives, label/size/UUID changes, etc. Throughput iterators in tptDict stay live.
	clear_caches()
	output_fields = resolve_output_fields(output, exclude)
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
	multiCMD.join_threads(timeout=_remaining(deadline))
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