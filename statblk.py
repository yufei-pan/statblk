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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 54):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE'EA+5s6&_Ti3^3S2I-:pLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%HJ57qq1/\
*gL=8;jBHJ\fYg4:j%to1R4$=%aO[S5W>p`gA_=$'[uT/?.1N_&PE1HaE>4:M&BCBVcr3$)%gS.F#Y0U;'G@Yf#\iaYMX8n@Cj7`rmp%aCrJu%B[E*^L
S#9/4@nY7\_*&('7?"ObNK^I$nStm_t)5D!<$XBk]A8FSldVFqkipZ;EWnA;)9(JK#j9Pg8;XEEFcR&MXS$i8K]2@Z)d(Fc2uC*D(R5&XBjOabb#nGQM
s'jk<mB2kgSK<iH7Up,F9L!`X'-4q[s(,,!OKs+R;A4P#:D(9F&6"H-::L31I>l>F7FcpCR'TuK\)3iV_%ms=;+MJU^li"a#5qt/XYPkN5YYCn?/L"Y9
`YKd2^$XX`_0C@\.Y8GnU'3R!cE6c><Gj@T/l.dA@#Y@'89c>!>R>8f@b[+0An>r^6A/gX)W)CDc1L_86SU+RdgW->rUPk!WadE/L9>fri=%uV;mun'5
2_H#a9V4FZFU@>WEd%CE3T`13F,*D5jnV7@&%/X_r0mN$m(uMs3]J)]nP>G)=>E$<Ka)@W:H=qDF!e(2DrId6E+Z"C:Y+AtXI::L\,=9=c.FfG`o.dSo
%uH7$0.2oW90b^E7BeXP1$YdbC<7@KF!8Hc.fK488]7m6(LL7^F94hZMZCP#G-g$#t$[![OrtHQ.dNq2M"K`io4/Aaq:)NY%oXKqdal!if3T"J\jYUMa
LjW./0YE:)=T0`+ld;^/R@33e)T89fst(Z>>?q\sFNgYoIo'<_JQBY'\f>H/hcSh+VW"%i$#@LOBfpHSrTj,-6r$,u]&;aj^I,O#&Fr=lD>U%4ZA3-7?
qi(sCNJI;W70*G&[-fJ9+\1WLo/`7\E(]EH.DE,H6&c&Tr=.K$ssRlF@&DY@bmMPH0Y\$SeWq'fLJGZ'PU2eN-Cr\e-k7O!^?2<R_a8MG,LUBC%a2C,q
SAMc+^H?IF$4Sa9OX)PksrN1<9etSPYK$Th^bjGkW8712[%<ZYdkA$<J;>\N>_k[_Yp6\(PVQP`uX(m+Qa5')Bs"9*sVJUue<mZRI4gd@bSTc.*l_DB:
]h'7/kZ",I.#!O.G)U3M5tT8.`JJD";p:m$m%nY8Iu$MC$2!"*5s!;nLQfud%'YF6[\%AYF<WT5BTWhm=(+nL!;kS<56m%$-bf]iiT:%>pacJ=:42g^I
R+Y?iX4m8HhP"G_nY\R!!DRtrG_6TnSfK5oDGg`ZTcb$b%ENX*M&/WqEj[%>M)d;2@YIgMt?*i-Mm0O:Sn_4&B!*f;qPpgi8XGMl1/_'N4:Xt=aVTUNG
`XH^:h&2_+Jn[T$(QZ@rEcHd^Y1^4]"P@mI,e?W\Lc1f\2P?r8F+VVKP$b-c\gj-P.;DV:K\VXJ.THKuQV#A/,P5:_2uYQr(g!?>BcXk=3_V)KEm)WFZ
6]UA<LG68SQB"@T&F8Ju&GE8C\P8GfqgJK&s=c?N=Jo!d/EGRWuPqt+D1K)qNo96LCM'Hpjj2q-O@p*23uq3Yb[X8bg%b:%5'%3)%l=a-bnWI3`1HLd^
X44'I,mF6(A]'0%1Z)gSI_[G31^mBAJep8*SGBp5@L-?A=K>T+:rAjmV<L;IH7B2Gj@"M-P-012P3@)(,cYp7Sd[c:>U<E8FT@NILI:=]1%L8X;6(^TX
[;7o$RigVuVS_RuedEj>b-nAJ)PNLgi/SJd]"p9:&jj@r6I/6Ym\3DPWgarahNTc&=8F`aY7+t$M#L^0TRq>h]-D_SWGTHf>T@V)j@@VLUZQeI1urGt(
6Srf[E@/sX8Q,L^S_kbFm;c']h-,gXt(I)(Y'?=:37U^n]Zo%ggJt9%t\;t=C&jX-c@bf@!fUXYqJL2:<ODD;,u6l'0*]THKO%I#FjPk^Eq<e;5.B![t
EPS/frTV`*sO"Q9Toi!C=lo=J%!*b'D6'cP)NHZ95o'3G``H9,pK22:16I6FFe>Kr!AbD00R)ID1;-*8d@e-Z$sQRn"U2fcM($\H/MG!;2<A;-*_^ap!
V2AHQVu,`Qp%/K.(t+>mkgEfl>O2T#/lYDeXpi`!+k(*(!a/`M6l$Za&*8!VWS3Yod4'<G7-?&6E@ZGK;oWDJ$3Cq5>i`k6T#F,1]<^n/418o(<1"76;
eSY`kiRVEN_=WAE.eB@;*L.I)H.t6=7UgI!";T+cDPJ2:LVpAmW$)>`\,4/1'"m:"NL*jD8S0hPPVMAp7$m*7(8oAab=4LNkXZ%k%+r3\;[3NYB*Hh+'
ZS1EDot3U`.]4S.;4h#:f2R0-PlOet!e[Lj^gmi"k\!^[:;QPkX/`9(#/\nZhWf,B;Pl"eI)Y5j+1u1haGpaE2]@S0$Z??!2&;C^.u,'N6at@K5Dk)ab
R[K2qM8Y,r5PnRhN/bH!1AC'*lBmo,D>2+pnl(5Z,$TUo%?05,;Np:AXsSb?3tgd6F1Jc/a"GKN;^lp?b?qG+<'<TE/8))BSMD$*^Y(D-_7?$6m0R$aF
&oP4_Vb=#p#Y:;C"#$[$9iD:5Z)DF^mBDG$drZnXgKd'.1eUeW-j-F*J@<UC;&G$o;(kN\?t@n!F+DC!tc^cmoYn`aI>RM+*%![dX-oCraelJ:#u>KI`
R1*K&j#a30,J\g$i/+"mlg>i\Et!Lo-jp^-sFb<?k3g';e-<Q'X<b\J>3aU+Yo'[gs`WiPh#S0L9Wa3BOQl:'6Q(q6^EA4=ru:!*u1O+`:%,rZn-eT@)
>(=LMO[rll<X[mt#l?h<9k/'9`-o<RI1ZsAa`&+)H/s_00b??4kWYG8Q`_'1Z"TnTmBU[gYQg5G<P@T^1)OP<d4/fa8$"bFt\!u5?UHUD%T*MRe7f\;]
n"qjD#b/a(mXn!Af5A?e[2<R>i\j4qr%34mNT`87!eMsJ!kP_A0,/W^V#e@9q.[kO7=OlDEsut+#*PZeT;)Z?>C@("'e'GpN49hF`>k?JR(]cVhjDDs/
GF12JGj4h.*_)ni=>cre2:J=_QeN*iRHt>&2!p!\oQPsf?M`Tj!!cg)fb;&BW[mKVp4"OIT)*fQp_[L`a%qH.n,tK'Tqujp4hTS`]Q*GK#VnlWBBoK.b
pFeJn\["::I_K?&;:ORA$#Sj#:Cc2Dc;dIu[I^mQt.?F)NSLL#N_IV0d?S#F*L#jWE?a21/f7d25hsKWV%!WpTfT9kn:QU0-^[1Pnl8*%8nu[N'0C[hj
j2<WE!k[2ac*4V2#/3CWPqB7TTj/R9E&*nTiaMnL]NN):0Ep2hU3Vl5O-;*/M21"SB92=gJQEEY@6+L[,.'csN+nrjhC08[ItlWB5GkQ'(WXal4P6V<U
C;Akf&<Z[%5=pRn0ai-DcOtfkK1+R&j-qrRkn75KPL0D0l+VsYr`/&f!M[JOHY]/t$%,&:\ofnq&LilJ3_<!E+On50^\u!1=baF%01^Q)6,MG*GjKYV1
/G22K$s:^s#c/$]"LQVl+CiQ>CAZU#'[1]n$.H#sB4\VdFE'iJ01X?ghjOU8gRt65?_9BkbAfU(r@qZpna3Mo$$qBU<noX.'s-*b<=Y`4D]r*?JnV'^\
*c$aq2-dB*$@P^@haCA]+44$N6fs/FJgFcr_8J?7!+2C)r-S"r)X_t5c)sB^gosL$Fr_hdgTOK48NJ,4^>;Xc/3i\qdAuC5!#Rp[o7eVG%@Y9ZT*Jdm*
7Gfo,+93XV#EmTj.F/,Hu@['80_'C*kJ:!;6b)ntAM8[o<HYC`frVE1k3G,W+jSU6A,sYsF.:R6PH:C;$7PSdlK%Io4CinX&2qkZ"[HKRnNa81_FF6>$
B^N*RF5:-@7Q2*Zr@>B2:+M:[GXe)(O(]Nn(+."f-`Fd^%:$5UqK5;75Vm^&KuRH-dnU9^r&`82`%HfH*HETY%b,H6NGR4/#)<^219m6H/9j^fpp.QK#
U/@lk>i/M$D`fmDg)<dn1bS!TS=\`cD6^iG=Ud>+/[7aYS`K2U&;.GMN"7+?GmEeWbM/g8I)1ZZ,bG4;4r8Y((;gK(#^fm@VUb5;P]bYO_VG=/[b40@=
Siqf\B+>@XZLOh)kpj"RRR1`#%,]9Z>:^R':[mI`H]j]#2^u%Z4O3\!qs5'`H%:1#(mt)b/@.EPj$er<GgbLnQ:7pBN"D@J0Zb9+o_Li94-b?-U:hl)Z
DW%*<;)mlj--r>KU?Rf'>nro98``\QFV9Oar6OrL%X%F@I/"cXj's./a%&Jl*"=Ig<7TEAs+u3g-A>HTQ((b-nD6D9R--TlXqFt8$\#ERFTRA<ZAG$rN
6)]rSc>eG]XtheijutKop0Ap,@;8RKB$gZ!u:(pTi&1,F+"pU9Z-U.P/d,`Pr,A8UAj@-tV;'fIR?p0Bk\VFL0bNc[7,,c#ktE!^;`]HlIg(in59L-G8
0YT!Oef;?NY4^L-G&9*SVO(CFRGC-f.:@Dco1$U9i9?_$n!$RLme+:Yi%@*^]l<_%7&?+ODLe`1`5WR0*fKh4eb?OG9!^$YrIVi)ZXmGQ`)34^`'UpOD
%VXWV#]A1CjJ;Olg?QgY+ML=DBRU!;G;]6U=PP9HRgiud[%_"3NbCI?SP;+PFObE&K@>GHH`Vk`GVR-5;\,X8+''7Ih]@>2Z.i$]kjg:+T/oDoRV:!F8
[N8c$Of/,r*"kMF<6o=7b(B=]2meGVM4sh;<ZG"-.=$nn3,j6\b\aRCG;#>cUj6=9'a];N-?6=Rn_UWZ\;dQ%KHmb^g4rBB$Y_`o6`.'%BrtG?=RJ)OX
CV2Qb6"]GH<s>@aHWkjWSY_t6F'HCg2%nlQ9]!'g)^BFn@$6'R2,7:*p7aRLnn7A8EK:oF\8*J/XoEP2j%d+S'\4YdGhDYs#U9Y`T;!Wh]cWX[k0;O;m
<tEGf_2<:,$0kH?U8H#5sO@lk%IcnYN!08lpr`G_8"4[\<+[cUBAa_<lT8(b0>Z\D.KWgg"'$]uVL>R_RKd\WWn?E6+-p^I'[cF6%?Am2Ldt_8M6$2m1
<=8r&$L<DSVRBKhuJZcnM3fmH-Ud;M-1HB1#Og"gP\nt2FDTLej+AF%IK8p0fO.<C,?AS.8g8Ig]eJS78HM@anCMiN#3Z?;0gf&2an:Q_Sj)Rs75+FK[
kY)'\^cpi.B9(BQ+kS`Yl3*L2[3G(Mf41]L-%ceZ9OF(n;"R]r-bQ#[A6<iX\=o((YX\$Cj5_D9U,)PfA(.DdI"Ud:/4ijPs2csf(8@(a-,n+"/Oa)!2
`kO4SIt3/GU]1^0a@]q6/*:;V%%hn*\j@kh)\7R3rs,YW(X1>"e<)M7\P"@3UEDpRF@[IDJ,QH8q]#::?l"WDn=WZ!JYi8<rP_cH=bVqHV,)NlJNmG9]
!?=4ZIL//-hL[?"*RF.Y:6_f";hdg_hU^1nrBi>%#TNj+@)@a\X6']=.hY?gk6EEP\onA(et'E04cL$("JJj(\7nDKq2sTW?(HtY7%0@k>M"38XY/jBE
+KnTg(!VkY'TJ:3=C]ZI^Gm+=qg!"2\8t?UrHUr\=G"BX-AV2,`Sg!3#FP;<]OL=e71a%\#LDIglGL8k"YURpBg+3FjY570uYs4;)qjK`BiaAu`.Z9%q
/kY3f"GeQ5>,ZfhQ^<.7lFI'8('-@kLdQ(E\f6!D&FNG?7'\`/Ggqb<8KNB*YB-jO2:+>Z,ZlQf<]O9if9/\2c(-E:HiBUHK_V\WenLuBS5@qcP%\(.i
GS!X+MWAj(-o6YP$Y_GIgS&Qp&)b_Z]Q?cg!rk)indZbgTQc\TdFU\W9GA:(WYA_>s+KeBrEa@h/9)so]:iSXH7LTirQ\t$lO^/n=9dQ#5,O7B0aIrH8
PR5S8TFPn;J`NI`WB.6M6iS[adcM=R%uRm(HC*7;1)n/NWR4'f!RYDM5to;p0SDKG45d5r8hPh4$!+W[0/E[,q,U=?9?<tBYXJdY0lWl1AIkFD,2V%MH
fE8<"'^!b[M1,GKJF]Z`Mp_-oQ3,SOtlob"k\sH_05i2)',Lhq4'Ri;N\ek/.ZpJ%CG6.c'KC_Gu\J[5mJK[S.;2+K`qAjf#fX$bp4H$VR0a)\5D91?m
K0]-:m[BA.Mria&@WGH(e.)WAGJ$7+Ed@!QoX>HAQ`I,J6*i9t>6Qi8#I[oDsD11\<W>'YrZJ%Jm:moQZJM8=lPtmfNBHq("/ugT\b14fl029dWD)0*"
]n?BC`"N,-KQ;m#\,qJgNVBqt%\N_\5P&`,AOVrumG#esrN/JA,ZH@t;R)`Ga2*=+no'ojdlZ(bCB)9CP*bX^SCIMKe3mo[U(L5b:mGbg#6Ck\QI)S?+
fg'7[VhnX]W-1<?Xl%IU\Tnq/WmdoSf5ocfDDin=rr<_g^5POI'EOdZWBq/$HKm*4VkrTE0Q#'TU>KsTbGj1(\ig0"$[,kb;ke2P&0;V!!oXjXD(uPG$
53kB:9:&;grj#&4($o91HXCs1&Pf^4S-^N!2B*II5lY5ql#n?/dFq^gU$;8P4s!*KR,fhHg_Oj3Y:,m!-XRF/>()cPl/W`Vq&k\I,;!nm21K3N;&C!a#
of,)FeAm_dfeB3XIoV"ECqKB8jc.1)uph`6eT*)l7qGl(1O?dpEFf)pSkl/7k=DPR8W+*Aa`t3Qpq-:3V^0\WV,kB;2h?"X*Q!L]#W!sJOI*9HoUjTb.
87P!)`6917s99c:@77^OWVJE'-ALW2r]rAY]f5U8$mYFIp."K%u!!RU@#7E0"'7NbEURr4t&u<f:oH:`U[Z[hF:u,7Suoh^H?/iH_g/1:5UL,35eS_PL
kB+W@JG<L/j;8B.&-X*]Eb4h1d[e5$jV.SQe*i?Rd0j#*WU84]Bo(F&qMj^.PAB5"-%`CHL7WuFW^b4WC'V+fI)OJWIrZYYoF+EGhPB`h8IM]EPn-[g]
p3^1;Z*2gVMgUoHbIQ/@[%Ihh)Wi^uU-YOWG=t"";BSs9Jd<:oN\l@*,6?r>Q2R:TQbTI%LI7h1;4XqipD/f'4'ar.(<!9tJ%pc4G?KprCNH:X'Ks&PX
]WlA(Q`\N[L?J>[e5dX$hLCB]<WS/Z!AD?325jspm+k<:=c%brA.IMQ'"u)p=MLV)#(L?sc>^?dF5\tqm3F8u>)qm@fi^VD.W$dqC<1G_&spE(Ypp$62
BV$YnoVrX/m,M5jmE&).X#g)RcNoJWkOGbEXN5m4eINF8=>RC"88Z]GLP)Tl]iuQgH_$#^IA8pV'H8iJrSVtP'O)24W^^",Mq':9$AL2d[[VPZu9(l7A
o$TllE?IX)>Hhp^.SO<uJ00-ET8rT5?TC\+uVB/5^C0<L-4N)8kcC&q]7'?nV&Zc!eT9jPJp$+SJ'J\g\QWSr"E_,GU4Hm?PO2;,SAbMcbg`$V5[W=KR
#oA"h&:=d*!cT-'s(,o5EIe.lK07-VT`lG8PTRSLmKfd@;"9hA/giY[/9O;)]Wm+7rBrJWWaggufC>iItS/[J'MCZEp@^BsC/&0niO@SYJI*^Iq?SR>d
`!FCO[df<2GS+;e"3KS'kT:SEkB\s6e;abj!gSO:Hm+fB`-"mMC,n95q,T1pG;D:?aAr6s+q"H%0*P1T'bb++r:Q*Pp?Yf4"nL@(,UkD[m]h)!3BF=_3
Gp@YeU80?F_T#B`!R)0N0d_c7+UT;:qN?8sNVu%R-`%JeQ86DGJ"hu30rg?Xr.S\hnUSs'2,bAN?^:t4dV';DFs*S-3Q*(320c+,U1)2p&t5=6@>u&lq
tV!J<s.Z7"!>>q:i1'VFBiL.4K5m*FVA.q0If,E^.tLg+ujV\,HkmD"N8ei!n?!T"B]]FFhj6H,<U2k2"!G(FN+2he&W.01lC,XOTd"UEQ)t4NBO"D&P
E$[]qdiBmdiag9LQC'-3ID`Z9saqNLpieJ>1e_hHi6VKlZ"n<,O6C*b>f]qa1T>'OkBQBoe+'!>r"3Xq-4iS-Y(4n?=;pJD[qRTBeF!#<nY42ra<(GB7
A:;h5C:H?>cuES/</Wsfib(\8)g*?ZPh7PESdcNRpK/m.N@F[l7+Fiqd-mnm9lnFsSMn>`(/U?60+^>CrBkX%sL.gL8@eT3akC$t<^r3F2;no$0Wc*>G
+bkoOO5B..9>dZhZRqQjl9^lVLi4nl1U?\=XYuAl7)Z-JeR?7n%(d0nsdbC:be8]MMZRO:D2+Ps6R!F%N]Esam5"efB$B,4pbAg+_6:[Vp[dV2c=Rede
V/)G"r5K(00(uha![b;lP1f&;&:M*._`3=YT<3K%an:e'[)8HTrCH!FPLV]c3h']Nm!MPQ'\!B0X`n!#O:Y4u_LXTMnJaKFhY/Q#5@Tp05ZgLX7/_N2(
iGc35*?_";Di[O!Kdl"i'L!,%r4\ViD\L#cV5d!TZe,a`?-H%i1ni=FYspP>l=Ir7"cJS[32TG#$V;[d0](\#_^<g4K'qphF#iT#7'hIfWPT35!2,)\j
I(6TYXa"&rJ:Y7qujk$j*bq[Q@VY)1=J^M#u6P![>F"G,6>o"gp'^.-9;2:m#0*%s&.>.A`/sj&Jm.gGPiN&L?H*Qbu$u1A_l<k"*p_AVJ[!(q*TM#T[
C1#;Qo!STgZe#cW<e!?Q__[(h!>p,O1/;$uBns#gaQZB,>[a-8Z]hmG`IGdLeda$a>G2(b=m!`Pd0M/$0G_PuYt(N:V(kqMFI.Hh3cLY!`E)jO1d_IB0
UeA"#jJPD3u/nLMb?;@/?*kYO1-pt0'!1,,T(a_J7<kZkr)\IL,nK9#82TO/$f-r0;0HDBXOk@;gT^e(Ykdu<=;>K!_Jnt\;1"p!(^tdaOoA80gN>qMZ
Tj[D'[t%AdFP]"'l8]0P)Kk"X;gM7N)O(gZ@I>:'I!ou+Aa[+?7dg&lZ'5N0p*u$&8:dYdTqnQN;Xg*qm\Z=+kW7P(<(/S%S'B!VO20Bh]'n)qpd+9p(
UI3QpV:p((WWpZ.BAa*eb/D%g)uRqMkGP+Nj-)^35p%ABu95Yo$C;Rf-nQuiRl89j3EhXU9i(]XhWqR@J?;\b$N_s>7nG_&9(X_&X<nf[0=\2Bg-O()^
q?t?^BFfAlK'A$/1%I?Nhh-"\d<-QJ/dr#if+belhu+RKM5b^m&(tJ37$[:aX_IRt`l'`]MI-0hl-6jtP.RgfdnXq$<!I>*FrrX<uNL#E1(#1>[7Xh`=
ndMF>_e%A-bir"9S&JLqX$'u:OQB),Mql)CftN6$]aKP9d]_'J=T3<[#"+)CdoR%m<=8)grIYc.@]]kf!K!1.S/q#h&X(2.1"ld'(_Wq.V0^MR#fN.KF
p^ahf^a6pCCGBbP<'+ZrYa$<1Q(r_A.8+mCAjZJ%TVdbN,``@S/RdLL4k2<QXm*LAf;AJo314sCF1cV%NMe/nt>h>hB;=r(7F,5Q3b.n08@O-TRFtQM6
@T3iHT_P1nr'>ksA[^i5?l<`5_g<4gK'CBToH\8N`a]\S(#2)ciN.bcWh[FJdbN5@X]OTA;O_t.[_F&e",IMZ]-K;&U/9Onm1q<HHWQ#QR`]s-<aG/&:
c9Hl9;[L*O(2P/rnLtbrEMbuI^BZH+Ql5,llmIkO@(0$e>*g?#6T<?c1JlhH;rJF7PGmp<MJbX1jB"_XBp@WW/e=m\S&Z7<Aj(^Dk#(Vk8^p6l;GS_gg
sa:H6jY#=U!4b4GNl\=5'C&8(U+e%[Kj`"IHg;etLEM%P;".@bE+nWd:P`eBhQ-b0CET"-*Foe5o($mhn\;CJt98n>rte^40GCecKlI3r9m=[$F%3Ghe
)RkgseDgUA#"8-/_C(0cnE^0Mojjde[j7?)dTS#)N@l#;M_/^t_2R%<kj>u-:iQe3;lXtZ`)C]!1E;Xr.uG8'n[%1L+"r&;uc;LUr7^nnmn2Opt3W%MJ
ACC*>.//"sZ^'@PdnJ"'#2!7@??M$h#.=n.?6qp>=ZPLpd&ZP62a:YM>jrJt`$blT$k!b09*talW?Oqc`W#(SbJN;JoMGk%$1]3#%748!U@,a0'WrNV]
-rgQ/9K,#u6OR'sF+7K]ej9c]oO4B&OE"ne+W'EZgF^Fe97'PK8Y)%gNKft_p+9NLal;8NbKK(+->N%kpG1K66a?[CKM>^rmIPoGHX`./rHbaVHn`>JL
KD6TI#[d6XUf.JZFc<Tp8/kW^!cKuP$=2^$f=`F[GR4kBi.$"7MW"Se!&CYNQ>J>EBaSR7Ymf"+^GQ._sSqiGG2`dTHJJ]GEDuS225RaQpo<=&8:#bR3
OlEKSe?j%EcsXA_B`Xlka?.Q?7CqRimEWM3`QF*SK^L?abKk@:pZMM^W4e]Kr2B0;OImroS>\'D7,SC\nab`0+2D7mn%K#r[RWJqdod*n!;9%%JFY_o4
Z<Xai.P53eVc^b*%A$LNkdlJ$@9Vr'(iF3hHP[Kl'hq;Klse4CjM"YDJ\eZMBFXi%!C+or`JcrjMQ8`?/[:-hVsTqN+:=E%j'WY)>S#s/56oeq,*Z*Tg
p$6]?`7(HUJjtd#'^UOB#hINQ!SHfY$Y6aI+^acu5O7e2GR,D\CQ_#N'EH61klGhgZ:jd21kkY.ME^IaqV.m,VSVNI^(WnPh(\aJKed';!/,0Y`HNX'_
H4Pf_s,HtMZX5.,hO.mqE/`muT2;HWM7bWYho;$[ek"f$8/F1T4UOT:;%'l>OXe;_bt&U.]FeH92(#8F1DM8WMToAbJ->nrKZE(CeWDadgeS4\IOH%ri
Qm1'DhMkF,Y]N6oP@i&T(l[3rC"ipaC(VKlSUaX7bQ9D+IM;b@gCR2\1a^MLlW[D''mU>s$=sDQH?O+>FJhpIXha2P^Wk;$1YBs34S^Js2.r$RjWiSch
,'K1(#cnN&[K%[Ng6a:aBDtVb(b)4?FiU`0VOpV2\YE()s)EU_Z"j>PG<2]!d-'6V*-A_W7Mb'%0@;mBs5jE5QI!q*^l>7!bDI+H]Z2H&"/&R"N".C\]
`Ng)S#sJc4HjCDA]F;mkN2iY-N2QG8mpZ"2W#Vn]7R1.%)$RLTC@>co9pLD$]QDfu2=P77iK8R%#CYgWI3B)Gu+AXL=9h<cjE4Qs=%l`Z#Fbo]$U@IFE
NJWH/DH.En@)\^96Z0Z-U]=5gb(K,k9/4BK"gufKnN-`U6m%0Uj$G4itO:?@6GY1(AG[?0Y^Lm%pRu't!]'@LiOU^/W0m?@BqI+L0(`=C4@bMqtLPq#D
Z\e;BoL@4:F:o!@ds8Kms,Hd2Fo!*:XOsrhA@!<sd7sHh"d",XDg/S?Xfsog8PrUs\/3^7A"Q(^aJHb*hS0Dr%K=6`nrrGF4]l`+9&HqU8&*80,l'BO0
p\,MppC'aS1@EgnqM+Q!%FmN[5*]LNbO;lgYXnABbUOZ;C5^B-p>HZ6EkP!>j7&9>?&Ridna_?TQtjMM)fQaXU]ePY;Q=r/^cOd9mPW[$0(0o]?+WmKS
s^5b:i^npN^!Y=CRH*m0=k-)Ag8URX`kcDQbZi\>2Z)6Q;LJc;h<#H^*8bkuk/&_G(d/r#65+N-i%`":P1V9cD!8_qi8l^3M(VZ[9*RoK&=1WRe26*\a
9Y/jlT8["PKp6al/oJ'A`]:YSgq0\'4(bD77In1Y#-%`h_:JNZ<:=cS_Imk?V?087de-_.*cDk[%1g=)1F?p@aCg>nQ/RT6o'C9j;"WS-mj[$\'u<'H%
1gJ%E6dJ;t\q)=8ho&?YQc$:&)grJ0/Gu*$Us!lQikR7+ih`U>B!l7TpGU887:M5/GUn*$]m%P#)8Ou_K[5GD*Hb3jXTb,c1QF!=SLf;Y5^"8"O;a"+;
N#BP!&c_\N]VoJ,+>4+b/0&6S&lQ0+dPln:1_kRfPA'1:c^)s(L#O#%7dEDsKfG$3BV78u7KsiUrR@Z`"'(a1p'(9Q,mOTIl<+r*lho,4J_"Idc(^mM6
JKqP&NL_C>R,gm*=B1uQbm38LXLNE<@3Q"J]9TT8ZaE&llsThXPX?ZDXk\7+*?,6MA/6'2eXlKean"7GiM2<+0;[7Q6`(Y;:Z3,d6?>1n)kk`0W'W?<*
o_S6"Ug#_sJKt1!?:M!G3YL]2<1LAX5m:TTZjgojr4%(Y?,o]@BD=(Z$6#/IJL%!rL"A)]K1;aEbFtAV.3qe*kt,pO"8s_Yjq8`[FgBg]$BlfD,l:LO7
YQ]hu[$?>5NGoEr1_IT55<iWi+Y0q`5MEn!b>*BsB_32o\O02((GL<]lIE4M1%F_7G;lR5;r*o/bhSNb'[/r2qrH5\kt_@).tg)a]V&eC\sF,bUq\8q%
DI(+HX_Hrr>8I\p?Hs`::D#k3k3TWr$\M[5#NL?Lod"j[V_1(^>q?$^u0/tt]'?)J-Zl`2NqEnc96!JnX;Rb1e*t6i5.?U9OE3*Im?<%cXK4+IqbI;+(
'jWfb_dFp-A1OHMMHlK-C<ZTpURO_(q],9o.u+_Q)D+1eb5KVD:pQ4,F)Y!gM0q]nr<jpIln-//+#7*X)q%T$j:#9bW2b072.2B%TU"NNWg)\aOiV<3-
5g):4UtjBMrhZDhs$_7$cO2=lj+I$Q2cQqnJ,p'rGjG131gbB#YV,\\JfW)l"C$1A6HBu:Ak-<c?D2u(ITWUqVOT3)<[kZ"?MA>4UI2$8Zfi9km5TYgM
&D4fC%!jSo7ONBb9a`gg/(OpW/4K*Te>MAjHBA2E(/"8]iEd\%Jhie<dK!Y<-SVVr'3qNltGM]PO55oqP"tHPNGBT=XqkIDLY!fFotYCW9*dOocklGG+
2&(,$JmSI;q%%Qnbse75NJXg)lSOTNI=14$c1i5#=R20"OWF*"mZ)*MBe?u"gm+0SE*IAH.fg;2/_@trUn>OGfW_N!RopM\"!aV-,cOef6]R+Zk&0o]T
,_7d^j;RI,F'm#1ibEshu<@AM`$@^$um,nGWIn[U.gI<eUqhpRS"[HY<C#acPgT4L6mCKG1oTF<,=LmH_&fu)b?":[Q=e^L@h<d.ei>-YEI'srg0uKhS
jMJMRn8AUSs!-%27,7W<B$pHViuF`)bE3<PYn<.n(es;#4(39OYk)/reD3tFCe+TV^+?VVcMjrK^g@d;D+L=O$[gbhLU+E.>%$0fpJ9l*(]h?0M.jXIQ
GP*;N9e%O2FHXL^-+%\_"B%bI0`0I!cKF2-K0jDn]&<:+KtB6Z@DqY/RJ4lGbQ!#)BNVV+FiS1mcS89]e]AiI9Z4K@%Ro,E6AR<E>u&HlIY*I-$Tq5l'
Lb:X]'A([dFG2oJ..XL7e%8UMp69*<1/CgMEAZ"eM9LW*2!HkL-H^1c=?r!,$^(WoF%QdAm;Zoo66K2j*2rWBSH`C&b(J#aYAJ1<6Zcj)pe(@QkVN4OC
@?W_,^9lPlVaEXl^b3K_BD\n"gdFfj*h!.M5u93a]DVbHT2Q^\qI`5FRY"SIVD7CcjVP!MC&f<g%>auZoR(f0a55M5ijJX8ng3oJs^V_%7eKiAp76kT2
8.siq%]2@fEF4j[sA+i&L.](C`OZna'ln1j-I$E^`Ef?_OM)0ljKlHfFfJZOs2XGY[\MPR<oMiU>WrCtuelQYu9).SSikU.]%(HD#_iX\4`0i*U_On>4
?9Uj$D.ph(-8DQCApYd(l&<+j>u_mf9.pA)h")XL%`"FO5!n[QVo@3Cag36RiSJ6IY4:M>U/AUO&p5t5J!-DAh'S4<&RK*S!tp5#*eqB<ha=gC(79fDS
_UUdlZ*;jM=3c&_#Ck02ujc1[35!9c.*Is+,I'*kW[bD7Jt(i1u3SX1oNR;/&9CDPk)%G,gB&q-5deBnn?uT"b6%5P1UYY[Cr`Cp_osW)R^'5g>"L3KL
Ylk%YC=dZ:_mV+H!S$%F&%-hh9dXbU'LH?XpS(NG(g/dNYn&<:&3AhC.,(n5Q.SL=0cia4\s>DeIY0;aq2Kg/k%6Ui-&!aSG'j'>h&?hND%@oa4n])86
tB!n;nZCPhhJ$k7,d(sZWW=!uqM4^24,1[ck_&?f7X"/c(5<G23>BZ_A>8L?M-lp]3mPlCs5q73%\ihPRq;VA[pP_H_O!gN^qhVEf.^bW%k7CKV#_a_>
^6-Z]?20Q41%fGWW_GuS3J,UYK25:en28`X$&.3D1>0D.[[0!`k(dKl;V8edUE'!5j73.;14#iZI@K:eHE;p/:NMD2F-aaaF3,,mtbI7)PW=;(tT3BO8
9jO^"U8S[lB]M0Fe*cp9p:+#V'T^mMaSYp5<Q:a=_$7ZeRj%n'AD9)&hJsL3.sl)e*Y@57]n:5hr7ZU-jO[CeUAD.VLd=nRL(\;j`BNZXQk!I1P6,,t'
Qt=P9e4iP,<uq`YMPE$qd=kD=KL='3,oJjH@Tn&E(ff,RQ1ZNW1-G=opV7SUZn)ZJ$hemQ8N]rkD:ZnZU`qC8>aA(VCgdVPJ-PAJhE,Wk>Q7(Z@Gq6>a
WJNq%$;LYa7LZpRXYWGQ:SbGmpUG%,0[0gVYV?aXJGIAZmBLU`iEsk[,qeTb`\[_j,l(%cH74I0"V!A2\D@;%(hc+,6g2G-qkc/P;<g)Ibal15d)6ePJ
m-Wd:@r.&Y<Z@67O;^h;[nR.s4f*:VYG9tB6KF)V)T^nBJn0JQYo<#2Qshbn;I7hQu?[q(q0?H.md-Y3Jkb\>i@=9(9(Id#ng(V@tr:"2V&4=,`5pIcO
5H:D,]_AePATuZ#EqAUupq=@m)P(SZj^*^dZ\cls=3p'#G@qO?Bh(#(7O31Apb;87&!lF"t62C<^^(blCIfF,>Ua.Dl4-Fl3S6Uo8UWrs&Am5JZ(tE\`
r(`W'63M`9&J4"-Bs%4%Z\JCf<\WtQBFZ!We(f84K&u`$O-C,6q-3YKZ'6dU[2(&OeG06FB!5=??,lB`>JpM<+o&RCp&_+),3oOZLiT(@bK]/3pODUe.
`[M!<Np'dY=`D.mMX?&6gWZGZ!&S-_+TcR>Q-ZX"P2/rKhm[:L+'jAluK^EbDngnEW2_$8c@r9k'cIL%e+483TXm4<]i+E/102e8lRV7oPiM0H'.`Sf!
&[E%1CGHI72c@d*NcJAE$4EgfQRKZP(eRs7`Y;(jPb0.@3hT-3sA&AW6h!KOb,Nd!2Y@ku8A+G3sL/C,%7hI-YmoACH)Gm@agLCj[padjZ5X[Fk/S*<"
X9!r;'o6SmRh^Po+8WKN<OkkQn'=C'rmU/49T>4TEj.4HAJi[q$hdB=Va1q0H\BN$+6+4eC78(WiU<:;>ceBOC0Jr#Y$]pqPK=/6NI+6K%<U'[+nUb8"
%jWb/#&JMTZ=IXEo3iq>Td8W^=Z7"oFWa)B*2Sm'48/5QtMh*7c+F>o0`rtef`&Q'-\ca%M?n(!pP7mEG?koSfj!H%.K1#_10\9HQfT31^iu4/)l<DcL
1MFI$J[Au`HDu_[#15`Dfh<4a\h1keGT\K;DO4][..]tqYo:`L(;]\QP%&ZD;4.QQJlf6QSGNAm38k./C8i&UBf`mL,YDs#^"LYrhUB_dDo4dAHBoF?Q
9iR3BJD1/B/I`gQ]"GeBgsu8^_#HAe9]Z`6[JnL6'V/tbH<K#!BP&F;b"=5hX,<mn(Y`>$,TKrqZd_j9(!;.f57Zp8o%pm%Js$t]lq!]$f^o@X'YqV>@
;LkNST`nO\sg$5lYd`Xk1l(^4rJYE.3U5;e/=eEf-APD[q5%C\)mZSbT2`c*_Of1sfYYohGe(7F0YZrgn5[VaW<h;4X[WqYL((J#m\!D&S<UB&TfZM"(
gd7[mk\/Eh)l.0;7nP2]U5**3S^nGbW.`YWeM+T4jr&`UOJ_pW!``B2q;30$D_!F%9<JeX/XEXkK3c%W+!"VRSY4.aH=2%9PDaD$2["jl(eFr4+aZtC%
O]LhbK)@pJ!Cd\@KkRU<6BR,I+X(_:s6M5RieHSu4A*F-bSttC_a=_B.%9#JlSihjtE_nRSm)k(Kk[8/cU[F$[YE9Z1QSi!>FN6neC\LWL\:WcuqPMR-
gqH+K4g/BXJR('aH'Lu$ZYaO_-1GKbj1d(mX%O=Moneo5Hq%fBV;q#;#S-sld7om>DEeR[C&7)d$*-L0,Rg.i1Mm9*`X[j0@O2eNW\RAqPQBs>5A/7)o
HDsrfQa!a:?@R;.P!]2,]>(PKLG0UH%Zj\V>uj(i]A`nKJ[pU(gbDor+SD[>ca3a.WatkheNpKW6`e7nZQ#M;*T,9V((5DU?cZZ1JIo`SuQTVM_i\-E.
?LKIVn_M$G_n4J)7mD>%6e0$(_cDq4Y23f)?K4SG&?.FaQm&-k#"c**U8"=V,Z;BB:t**p(=E62PGn3To!B>.IB-T>7k`13I>.YX6K9n+9/$a?U)??WK
%&(\A,#Hq4JrJ;.2Hn#"Xu@&[T(Ng*umO`-dh(\(C0dF#fSG@iJK0jLhZs0kut\&50YqC"WcOe'/V`uhB)>Oj1&+1$%>bU;8pYi3o0!5VJ?6/5s1B8Dp
F]84<Y\%^<3HdZ==VkK"?EpOWI&PLQ0QYRH^?T47jH9%,:8Z-h%h%Cg'X094q;0!,$AaHk^c@\'RbY:_57R7p*D=&>:'7XUpo<>VD4c\A?F1lgUnf8@C
6#MAiPJ.c4p5l`XkQ!KqESq]CoE.I/3Wc\?SEb+J3@_=s"'E#SAVLXR;o,2a+lpg-2Q,jUBpF.Ya6aZ4On@8p9(SYt/*^)5MQje:`9ZIW[1e!(mgi#mC
R0ll=/-"61`@TO#lgfjEs6Y.0XWd4,Rg1dKs"$1.tN,emV';`#sL'CK7d9?(h\Geq%>+Z]Dqp3`9UO'`;@Y_!!1M[^Zbe"FZdWIZ,C;P!WW3#!!HG.'''
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

version = '1.54'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-10-11'

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