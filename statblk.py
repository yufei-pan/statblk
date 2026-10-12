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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 53):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE('"=7F>)aNi3]:91L0tmLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%HJ57qq1/\
*gL=8;jBHJ\fYg4:j%to1R4$=%aO[S5W>p`gA_=$'[uT/?.1N_&PE1HaE>4:M&BCBVcr3$)%gS.F#Y0U;'G@Yf#\iaYMX8n@Cj7`rmp%aCrJu%B[E*^L
S!Q)sV)EkU$%'R5+]C&D34]WSp(1GMpjr?eFZUFBtO:7S"_FBE_:Fp]P1cirl3Lp[BOnN[d(sd=iG5[;N@uk#/s16<X$)QPsBk09+5VCTZNTN,I8&Gf'
NK3p;9`7T[<s8!9b^%su\coVp#R!?RH,5WRp01=#ll$L0DR6]U/mk/1.3m;'j9RpR[)9rbCfeui0V4/M:1r0W4P(-HKO0UX(.Z?u/NYGp0@'?cbtT)Z<
V8;dnK`UI+!>^SO;K.nL4k9:p;Y/$V<5nf:EgiMGZaInf3fS@Sj[Od>=<[FKoFSZ\*1GQa%D7eV3(g/Pf'T>ni]=4RZ/Mrr]T`WMT)fo01F5aV<dMl/\
SJ%m3H`,;:iiID26pDo-CmGX`9G&.:bFs08m^WUSP#d@nG?E$/q9:>'.5XRoOoH"+N-"ohrG@j#?:7lInp]r4D_e50-=nO1Y^eD`cl#Bq!<<sYo8`rpW
>oq?;0+T%);t`S#Nf99S,'iM?Knk]$%J-Bc]O$&AlMcA&bueFj\sl"b(<Q8AAW6DT6!6:U>3C/lI<%'X=f[Hkj*Gh$IV?+\HL>VKq\05s#N4XnSc>;=,
ZU@\Z-j>@0U>m0/,g#]nu=H`_pN=g+a?b.SCQX9!%ne!GmGtpeoLljHmrfloCAR^2`5$F23_T4:OVD=L!A/+i#RoW[WPk^T^^nFEn=91t[YA>";S($DA
Mg@:k:m+9M5Dr"e]qli:sNPghu35>tagG7Oo'oY%CNC3K@eD*t\1TjPV*h3t%Yo4JsO@C4<%CmZ@bdD4mJ<<[>O93f(n&N)^DmUOa?FR<LP[82&0WgoU
l'A1e./r]/+I`46K*+.UsZ"7ns+D>d*364G2\>0EgkSiKd']GJM0\XMsIio\kqEP`2@1,VAhTUDQZiD@EQq:o_h@_o"+S#oqn3+'-j_&VD.CRg3+Vu\h
_tL].TF#pj@q]kPUS0ar%5rf+[:ITAB:nTBE)?\4c_"tWIeC)SatWs,9`D1=25@iG3PX]EMP*>0PYJ%8>aZ:,dPH*?!d3EEID%pTC04o7EO,L_AV:hgj
NN>X=OV"V%%:\dj`Uc=D]_L)4teBDcrNTp^ZO#T'p9gG\frRmD.`KI_:b:\=^Di3Qon)@/;Y(3<NhBdmqC]J6S$&uqK3\pqgPh3!95dQYL[0H/b/%B(O
)t69WF<j:bVnu4tQ!sHCR.GVReYu"L;62[r.b7-)Hoo%Js*>riCS&kH7WX`1r<<qkGcA*UGg@E;76!'U-m\]92,]nkrZP#ip,VWLn7g&jFFSM18gt&3$
^?FFS[jM>QapShr&HjOJY&URce4$Eof(pPZl03RGK<]@uPC9/Yd`i:f?@*s$*o1]BCg!I7J:gn$=o-aQB$R2EOZ]&[;f$k]PY*ZhRO2<B-:E!aP@8rH#
a]8;`u`b5,#NCPmY[sa).HaYuA+.5BAY58+!Q&V&Y&mnM1muP\2*=/c)3GrpC+V[[4&Xkl^%Bo:jl1+PNA&$jE%*D9a7jd90>2H,'FM:>67-VJ_Y3hnZ
S@pURM#k;eIJS3)lsTWsR/gd'=FbBdJV:OEPAlHVS<'/+^h\nNoh'LhgV?)eo4&[UYB,3D:Aqn;iY\ls1Tq:@>&1*kpLTN*4@qdABcn];\mm=nMTNiI@
N-]a]F$hS-ff7!f.eiONGTTb2BqM5@o8O/BYeSh-q^jY)hjJ[-'t)'[u.;SV8iK@#JaF\!I4d5AHFta#)0Nk)TH9^rZ9Q0JP7B.)LR(,/R1B6dR7+m(g
RkQW:*X3")<0[$UXnbca_hV#K%W%;&GprQ)mU`kT67)H#K+^1HaG8dM/YnLUSDH:b936V*BLd;HtKjk7dQNNubgIa/qf`.XZSd\^XB_!DYlgjLt5e%mt
rl.2u7C.QPg_D^hLqjI`\T[NXEf2jrQfZP"GIWoUk7l/-1&N_[n%]*P[,R:mmtLD>QG<WZ2/$?oH7fe%9b^EQiG5S.0aKIXf*?%Q<,(@M6%co$bW<mq5
lrW'j:rRt14Yl?ckmfR7?Ou[D.6;$SqrT!QA(F9UNqVQT7dEAW&gYDSCq&TdfpHi#qk,fZ?c_'Qs:qY`8-qIY0p[A,X&?D8u;8osNWD1J9Tf^d;Hon2t
p@!b6M!2\3WMnVtgcS"`15!)=NO9FW%#X6j!7iKm4nJj9Bat&Ac(Zd+;kE@_?/i!Jat:63<3;\m-NI&tV3\[,+f&5j8kpj6Tp/%+mZCf8`)s*S#jGf,b
ocopEL.!&^sH*ZaZj'I0(<fa@MjagN&s5Y`+EKaO]'p*p'8_r-(7n7:IML8MV*E8@1Yg_6C.%`*F@KVW%0Xg-9kjJ/F_*F7[0.\c.B6@i_M_ab5+\nW]
P;<qTO"IIqD6P*Y^NG40==c7Wl-KUG9%O\n@hUQ78Y5hb&#Ul&8i/N#>Cde8bPY=Vs8K![$MN%Ho33L&P=df([<OnlJ.Oa`em(>V87%k!=!`r-gr<%5-
bCMe]c)OWt#[<Zd(+7d='iZ8%u7Xl)XtRa0C4C%:T$iml1m5S'"c#SIH][bQlB,pU4OAmtRXkE!-'X%d*_5Zp1JpoZV1/:HVN5-HG)HE:hmp(R><*2\C
WS<*rrIU]jt[Aa6K=?MTNknAbA4\Q<qj^<<65S$I=j<D40>E3m26:ogHk;0c`+1W=c;2FI)Lc2k[(f(pWe^OD7duKL!9o(S$TViS,OEZXeL3Wti5EEk-
+l8U\HZ>.9YjZ-maD=do/fMI\]Tk,#b7C043n4.>@Ee`A2W?E=:=?$sH-UF_-,8/@<Q`1:'^)GThG-hF]m15`dB?>bYFXg^^Kt@s6DH;gLsON--Vm(22
MZ-%ZPtp/T_tKF]JC=?".EqJ5M*8;/_giWd6Oso-1XjQH9u0g!WI`Bi$c,JPX1"?HNQ?Ri<YY&i/-UL2>cl;CpJ/""knT@$Gi(G=u^1&PUl`2mka@KU8
_^!s)F*:)O/c=ZoLasQ^(Lbn[\-p6+.h"=&:(EaOT5n?CP;1"`E;.m.[(@Opk+:jRSRq#N>#@8415nbPcprXSQDbO!c.#C$O,''i?T<eoY8rfO1037%n
+Km97:>RJRlt)1L`:+"UMLK_Q`lgr:Quo?2rOj4[7mj+fQ8o?YUmT_T]k&5WZA3:%&oN9aF%9&klIHs&7f&e]<cee"\(-E=_;NkTUG!;cS1-9@&PHtX.
QI6IHCH4n:l<T/cC8M6ZkA2M&\)rBctn$@1?m%h<.$X\[']lJ+-2CG0Oa^4\NRNQ;[prTA%@g6SZ@leq3/nce@)^TeZ)J,F#&#S1Kk'Kusc@Qgq:>Qma
K_BeG!+WrhWsE/R!FslE<nhm7J/fLKgsYu7l>R$HdI*nU;`@#Nb^IcVg[j#mgrAp0I?jl:<*`t4m`n,-ND>ZL,ZCJpgbhPo+0VaXr"'uLfXWE4jg+WK!
h&R/3jdX'/CN*=-g'<1:piMWbn\\lF]V[]+7q;je0Jl!^uebW>Sd.1o.`rM%G9HqddcNbUCHcKXKlleR-j2ljJpk)US?M+4&/a:dkZsf<.\ge1h"!qJ*
9@+*O]U=NmIW../,+/0s]CD.Z96V$Is1Qqk5B[=DhLJ"n$a/rl!&I%29\oAKTN.`+PioEMNM3cEL5`FJFhNN;j&/`*BYR^NT`\N,?^QY@g0*gn0@[E5^
D4"oLh*k8'H'(U4D-7k"NcItMZ'\<92JG>/83FfM(L/XI0(PpF(`(i+"A3/r,K.\8f[au3g$LbZMCjHQ/9s(?RgG_Coi^!T6VmBoqfeCko$O`(II6_h'
m"-5V/`eN:if_?ft_),5*Dgf`s*[+LcN^jS><'ZL2`n:.t:lP.m)<Qk0JoKDh)&9L7(W+AQdhJ>qJ[&l?*P'/tM=_rF$YHJeD+`3CZ8_$TfN'Z+=2I?M
')li)6/40&Y&'+J?tO@IB+_>pHmI,k>.O822E^Vm_0ocj,X0:T&1Y8YOhu]>+tF^=#m0o`60o/gC&lO8c#)icg%>UP_a9\/4fqV^A:np-a:P'*5FIN`B
1;??Q3PK])b9P\j@SrJdP*eT@YGr(6+j12-DD6h-T/5F9QW7J_[d$lh@Q:h<da5-02r$N5"`us2f-fQ_)Kr__`]=D)X_n2%&^4Tdo9e5,frob`I>6=+@
E>](l?M)&JLk7O3dV/QD9EG=V("MPk8o`ON&="2_llt[2ZE?lNut>n=+HGM//Tp%45R@&J@D`!$(nEK\R3G&*Dm@#^T]LRbM01DX4`$$&Lum&R2u(`'m
[&r6%$,ii@DueN?1gd&00^Ea0HoH>bEh6ZkZuN7L;)\pb#0#j5&kh+i"<ChAgA=kp\jRR'`6bUdB=-g>UV9H49"Ks>q>5)Z&-:Bi0LNsXlZE]l>Mf]j'
i`5bl?o=0fq1!-\NeJ%XLmo*ASQ#@kis"$K5D&04ejn$j?82K_;S7<TY2QW"DI;ONc@AP=qKh9nnRFe1ch!4k$"PZdbcl(f%lY-i!&2<"9RJ_nrJfsk0
[e8)2mEp7V77,.d:)t;)CDAL(@\ePH**X?[68"o(0i=B)l`nUnT$/g6hm)o]W1"aTX'&'d+]uE^<Ch>"X$qk:9k"(Q3^i0*HX)f-:,::j1LPdsg6$-3b
i`UmgI<5L2$jVjhO`e:])3!RG7[QfZE"T#W#,C1OFpoGG85GmMk2i(qt%_k\NBYE,%gSFM8j!BM%_0FJs&sp6'=db!)t"BT&>CbTC0rEQbcIEaF)nm6.
9ltN4jm,#I$T=@$k86HB+KM1i;7PM55"r7;G:/6!M.`kI@jB"pjF.:(4\%o(A&EZ^RSQF'*;c'Ja]9j`bmt$WMdjL;QX4KCWZfW3Lm;/f[TuG\`HV>2\
/d=]6Oeb.(04^o9L]<>j?XWA]pu+Z8NjJAM-7b5k+\V'.QZQqNQJ4,mNaDrsRGHIGfn$3kF,Sb=QQ$q0M0X=]TF\i4X_DUfeP$/-%*3]+AXSg/39gc'm
!&V9\d5UA%nki:^5_VNjCm]3e+_CNgQ,RLYPNOYol^Pg'-#K\fXnD`4.H\`!`G]G,,6KA'g]kR25r-t$f8E7oXBW4N`;j2\Kfs6970j8Cr]H[BOCcP4J
ETWV:i`>$OW7a;\f.qV'adXlLg1;"cdhjbN@o\\E8X%:HrB&^-c;m$?'WfJ3-pF5].'W^Li/]9r-&=!t2Za3(qLO+DDs*WMjFbXa+$R4p'/Ut!ZrrVc6
tUZ,0P32>@"0\C(jbF\GR!(>,7I1HYPeU;3FKlKg'4#@Y!n='d]QXdRfW\.rF?D%NF^?f2_XUa]K"uXk$#3,SUYTM_L$-;EBNgm4iR""\euV+Z=)tXDP
c3XOu&Cs1kU0nZ9F(4*U<QTAVDh3@gSLpSB'Upo4Fmq@$M[RjdQ9UFkj(Ri+G+ZRX(]GR"Fa@l1^S;N9F_SX;+4k2A-2aKW\fGBjG>98O57a/)=uTFn/
4##@K"EpCbMFE!O__b:ntP66aAd^Q.ojN!4(KL(OJf$$/aoS"eK4U26uV2N(nha9C&Sg7EUrc/PJ"(HPq=em*$<Dk18[C3Ljje2TaN9V!"MWd<K5RI%Q
jU)<aGObBrM[1LtNI7;XC*K4WFZTf'pfs7Q;>l8"A"X/t(a?TE6&8&Q1I%7Z:?KIh&ak:8<bAXV#.4,Rhofa_?VYiUe<]\a*n1T[340;IlpVoZULS8:H
A)p+E'i9HT#t6*j.pFX%5]Q3qDu^@&K0-lHdDQ<tS\nj=.OXd*,pi^8ri1j>ShF+t!sI,bo$<E\TJ:3!UBVg1hY^JIV^O9tcSg4WTPsp!B+BRg"!Ke&S
/;4rI=1p!hs(bs=9q872\:X`99rG0P&!,Z_R)Dt,Af)aRoE1r=EcUG<sWc.?mVW4)Vp#[<g?H[USKEr19.b]D$Elbb0j_]C?'g-DY-oBd`C%[X;^u1l)
.Ime;Wcg(r2I=gtrA(,ac9ZLVQ@Da+L1eEC":Y.I4IkJPlU'%:08_q6prL0sU^7,8;?]nOP(t"cb23[dUGKAh:@I*JW/F541H]O&qMkK,6'T`j%<+TCX
E>o;+b*dLZcQ+)MVue#;C$.<cna(d/;ON)]'is5l8/lrBR2>XPC1j3O._1a\B%.f9]IQ''\^E]sBr#pDiJJ#!M'Sn@!K>\g0*!@-f%eDoKYGQM,k'Kh'
q',f%&4H;G#nlV'>j_P^g.044;=oC)ipi#9FOCXB=WT3hDhufWLR.Q1n^h[BKO:jd;Z(=BoL%uS<)i/U%Lm]'D:K)2'2'2!rl0tg`6hV:[/pV!1R@^)$
KALm5I"73Go4`RDE)=8]7s;YCb"T0fjX_!8!gQ]%C#<>>YFB':m\(+G(cS>2P3g:oZi9r7qe1:\HGTaI[oQ36X4HAVZ_WpK,gm2j!9a64kjlta]FMfbi
JmFeW^8H9H&4s'>IVh#@'Pf7B8G6!MBF4km!rmE1g7A/n5'NlLf^XCM*CI5E1M5/&7jh/3=lNDb>ZN\\E/>/?217h5ANQ#&MA_4(!J!"db;BH%Zh(a/B
Ms#H_c^MV#g']p2530W(=W%3)B<Fm0th,%`YajqWq'k)n_F*K$Ga0K'('sMGjZ]'iJ>)1%]3_Q_a+F9XK^:_qJ:4M2b`J':bsk>cA2e'e7;B/)+D[MB0
XkO&=XCn24Zu-+GJP(8:XlZh*u>OaUFO-sg/INdt,C[T3Fg748+/P+-5t8W9%@P9+HZk29&e_ES/X5V.n\P.0l`R6/IEYg*trIV[i7l5u$n&9R:RqPTJ
`UBDJ_nsC9RiiZaO?u_A3bF_W<&X0Z\le.bQ[^RE"=joC2\iW'sE'(<_?\`#HAfUL\Ce>`?(eg$IbN^b*9(i!%.>u#KX*ks+g33J3j4*^rlnQ5"#/9BP
pP]D_@=G769-dm&!,5dB+BieubR$f.Hl;aY:^O&C3otGpGon[.0qOA>GdFtI4b9/G<@X.-<SmE0-HCkdF<Y\_[(e,iapLVcTr<6LE\F:!E]<7$9IX`XX
Z2AR"T'?h7(dVtVIB0(-$540p#d+KgS$/V*l;<$n3#kaU(+:$Qt>T%;$`D]k2W*D;6POH5I&3IW2+P[e@5`QQ>.m[#3/O"^H9T@E1Fq5g7LJCi-4SB6g
NP'6L9B3W-["2?K!i"F"gGC$aR5SJEj:+NFr!aEkp>E.[ctufFF$L58%D]/SKu&O1UXIT/,t+67N%GbF52DfA@qdON+:9I344:YbNe&\bN+%],uf[Y(o
_eH!ii4foH0Vm@:XH"(Rmd[8^n\A<%YmeTMC]U&>H6#RtnjSBV25_s9<bJkn738hl%S8Bs"D#Uk\Fi@X]NKR^+@imACIqogd"cC!No7e]-8'sZs3Q&#&
)>>+gOKP!ii[\0j^>upU%(/f/]`04n_C(8.9[M!)6]kXRMYm;N6d!Af*,kDg4F8B9'+^MP>:Ze2k6h(8ab1gqd?^P^8<&A[9&tG[DH8__j0$XJ56smVO
\g=Kra7K@D\4B*"++K>eR5PX[GPT;GR'MU^q1+Q<?*"8&c2\C5CcVZs&fYS7[l,t+HtX4TK4JuU,R's:c4bSZ6N,-l2(V.'V?RC_VMd!p:aWE.,sGQeL
j"#gc$PDfpPW]!"l(n<<C=W?+gVl\/t<GR*'WFb0):p_Pm$T[8!T>0dI'G)g6,SLQbdQJP).mgj@C0t!;9*&Q9Ti>]^mjm,eY?udp8RYYPl:CpC9N)3=
;/bSG%.F*+.1:5aAKa#Ab9\[njRrjjHk%[Rh-OSud/r8!C/X5$8u;YHJ.ionB>791\pqlh"W>165..&Dg<4A"#=7n=WgtfFb=97Cms0BJ0*ng`p^G(GX
B466H9SZ17i=q-fXB70s"<KRP7MPG&505&lOXHG+_(WY-<\'Sq'U<MB)))X[!0kpcY+XZIojE=3MB+HdAgiYLluQH./igOoHH4Hb(a"p)NXIu&b_>b>M
n('b6T&74ZE11PSc0I+U[*D:>JlYkd]YI9>Pj9BU7!7:4]mi_@8/*aZF5Y#MuO_SVWVM+c3,05QS^!]H&2T6dI9nirqT4Ju*Y3`f<oTi&=8&_"HQ^>eC
4.qf7NK7Xbqp-P,<%8h+#0H@X@MI;BH@+rZeb^6%!_K"/VatF24:k9l4P'YZYAa1o._ai7];*bl\GFUF1U1V:;)>(2IVUEu,Rco2:*#=2rJg97`o"^mE
."na#!^NUUIc=qMI7So5DV?6%^gO;R(Jq2q)0;,,I`Z^f-]oIf5@lYrTdP\'UdNhO3UTJK%eI!Ou*fR+:7.r&9!>u8\Xaa.m:^?N'.+r4N\!A>dDS%Fd
`*naQID"#RsS]o;h.d4^a@:IUl7"/LL)V9phae:&32C^=\$8L>gAjqo>XbP(NY6E'q?IR1aJ$Z:Q8EYo)%-?$?q-7":B(2Z"!AYVdF(JT^Ee*gn+K7&E
jt4.:sR21;![$&]j,nJi_kGX.YPBA7UBn-FnkW#l--5,B$66m!lbYj]2S%,bNG;2jrW1TRIo#i,XHK;Ytj0j7Z'J8L+L.^8PO5NX7FQ%(B$O^.tl4o:"
3"YCqAimCe-Al9"OO9F=maMsbA]-"0/$Q\Slaj3]EG[$`$2P(i88=ja9b+Ej)$&n7J*j1d6IJ20[#[U,gC!j*hkp7<]T.9Z5fN0f'YQc6S<F8(QAf%kB
rk;V[;p<Y8lO4N=(3]stT^([n1LnCH'[!)J"tnS]Xr>sX.;%j7O9F9Q?--thJ=6")8^[`n0j":"l5"M0XrNoF=W.,#i#d9kDYQHC`5"FC+Sf0)GE)^i1
"8iXdZ).9O\3'%qY/]-2W]FTH?)8^]m!orJ:qF%0ccBjp`,msI-PqRE,f>FP<.'MS<W8'#.[9@]bsgM:NXg6,etA/(f=)%)nsPGVN`*H`UU7HMA3_`fM
m^_XjY9HOk,8?o\h*@4-aN]0hP(Vii_9Z5n7_[R:';OcJt_Ak)<fI+(95LOHkOC@0meIeCZ(XHmCD?P(FeUj$o?l.(DV!Z"TlNkQhcd(4OMb_=\9/[uC
4*@4(kG6tC9,l]n$"Q#)=\:-Y:-Ke-()[\PF"=c@X"i7l%i"75]a37n\g3-c3*&'VOLYk\qp5KSrI4L%gf36[[-kbP8:j_r:i6)8QeVVdNYpplkT+g)I
kDO6ahe\cBrHWip0FqdrB'`<n?kgrS-FMaBlDJ>29SPDj^[+5Oga74?aYt-Q4ec+jDr@h=aiVgL6P&dM=WmQC+WE&,8J=,F.Ko_X*(Z_lB2*k,bk30N>
c_ksOAM4aVCFVZ`Xtq%A0Z>4tA;H_9pDqhETo+EpmR7a!PhJlt_m5f<n]YPH!N+r+;b'fk@.s9YjVABgYsmPn-Y[BILe3J/-d_A:4X">O25"H0##n7F4
Sc@c"jf#67q3Q6=Q9F$d#b^o98It]\a@&T(P4!)eWVdc3\ap3"&?T,78`1-+ODDI'L2Y6_*?4/a3+.J6S"5t5Sc@E>)kQ)\9"jXegDESEEk.&5W2^c;Y
le\Cb?sl0%4I%1`RmGXYl7IR](S9HZhj(0Skk!)n7b@OU^)TWR/2aA[-e$[@dY,-\GU/l?bd>T:+3/DcMYa'!PE%7K>?Cb2c;c>!5nagRhKU_(Khj\_b
`%!XSJJ\"\;OZh78U-Gj_GEDLD3=*$gFenqXqNobpBdB(BLBe02T$phaEY4:iGE1?]\!g.rUVUGD,8>7ld[7bW--(qIkjL]Y/pUErr?FTdgmDQa^PeCE
_=*bdmOCH'%dt?iAj.r@`)[%F.ZYKGOZe>D6qV*>IeR1CP9'"j@?9JI:ejtTQ0km:NZ3JjN9s,`lodf,,PP8F@ilI`03tRM%Ym<M#;SmW8pWK.`?AAni
FS4cp4)+mN@9uT'<sge;!ga:QP,H$;RFkDREt7cW3g<[\VY\EM^(t7SKqprp]1JtU6=$#bV!Vo^LBf+.)$&N!i;bI\^3D=1?j@FT8?)FS?<bh)d"Nto@
l(h+,]5s"*lSIpJTl/F5iNL/%h#P#7\qJ&VWZEdA6A_Eq[8r\p9i#NE#8b,/k=,bhc$9\XJ0n#45[oHjCQ'3?Z<.-ER.1g&/#@mI)DF-!cep4;Q*#$S5
A[6,X48e!G/><iFl;TK]Hua.gTuuBF.*9baDtRX5thm8RR^2_@UI<]c#-Ukfa0;5Ok+=#kY:XEmP;XU6oR9;a=6Wg`5sNpq#0>!7:>6/AF5B*ONpSFo-
J%;[^r8[goTL62.sQQ2o,eRrbcm:G!N;j$dO]n^B7na6Hj$BCka@m0s(ZO_isG3qX)$KhO<EELmdJNLb)qX?pu.WB"?;ipT[ko8jK:jcu,.2nBst93#R
.mk*"#dRk+3Lsl.0HIII![Rg8p0T@?CG,bUrOr38#b7HpsUlJgc9$i'b9hMJb2Kik\k7@5Bh]^<"hnIEj+*4uJ-7MlN;D=e1CmM?1aiTbY\t:?(?KB:j
epf6"D[hl-Lt0H)l<<Zs%frJ:s6oN)`?ET+\1gSkAEG;reIua]W@uoQJulj0AF6)./u;H+R[$07Ekm==(oJ<+3;oq&pK>oB/o$-DO.!SIf>W>g03n7sP
Z)hU5W;]\ng>D"<>gu*`)g4U,a4^?WPCPLNpVQ.P/$1_Z\K[jWhL9TfE0P3'*_Ifrk7q:N[JK3YqRQpKUspY<";C",&N2Tg?oS:gbs\HBFQd<'/]S=Gf
r\$"PMFi[,nOnjdFl5(2D:-!<ojHf2McTCNqb-2J$@.25j3,YlB2VFWfi$dW3)rM(.TGUb6.9EA!Ke@5R"od6RM6gb-SQ4p2;Jf%;T'bh:d6K%">[X^Q
cD$hd4'U8:;-;kF^X"ikRB;KI"TT\5!BFO-qUR+`3TS,$<l9m]mpX)YKin:aqO#?Jd:A23C*M.*E+2C6b:E<7<4*OPL5<*(EK4ARM)4J19$5Lm16g@Oc
'kFfKT]!V'.bm:`hpHs10IrG0*HpF,$\(3.9AWD?!23o&D2VTMf;dZGnMhs7[eBt?/&g4-QkiB')TT14-qo!?^pJK+Hdq6rVGH-L^14INM4B9o]!n$Lu
9\(+[/?XA9C8Na,%OX;+rnLLVqe?P\3ubGLa6:`0d5'+DJh3H,C#?0\JZur__#r!@$0a=^:3YX+)94.%3#7_32@_HObWHp-'ke^ubYuS2o5>^WaQtk@>
`YON1+:s75/TF+!Xo)"(\PUVkOFK^`^r7PZl&rYUDM80HXR/"@bQ1e_R]:/Q*4akD1RZ+i`NOgEdHfs)"IJ1&6EM]_@:Ljeq02Qj<ASo7_57tj[-eB<[
7(ZP\'(.H<8HEPh(DVeg'm>![)e&$C@?e^HFYWp&.J0<;^(lcpd^=Q1YVF0tS5=o>+"4oOcf'+`^:8c/Rs])cH=t2q3R,/V^oS.JP2V&UN!P5<j6j_;H
Y&98>VD,&ZUOiu"urLKE5HG??PA[:i%"'.4>sNcb-+\('aOfX3Lq.,os8qTd\%4hh)oeJ)WMq%IN54:'mDs4?qgh5b!;7pA^eBOeo,-s.*CD33,1cdUo
+]Mj2ufGgrt'>t6>a$C$Oc>J=8(35qK,$7?/"Fk].P)6!b@Jh6P9i3W.o>'3`:,6YL5h#>.-4K<KSliaSdKo/B\@F>amtjpKLZ`@?qop7-N$k=Ib24G\
&%4*D$W+s9IhI4>+*i9CNjbTp5%2Tmnl3@MG8DBHE5OXnB%$Zk]cr'(q;/CdeQ6-(aB1;b10-4gg$)8:gqA%QUUl=sKc(*@h1Y8;01:Qp?oE,KV3u7?e
HZ$nY:9Qnc7tUY92rT$o4ik/f,gNY9kYb\Z9OMd1^:XEk;5$5Z^1UA1Vue'nn=At61>XEcpKi!7&*]W5hX4(-E5Qd3<WA[)!p-Ol[]KZp$q)42gF<@"A
Onero2^-7kdgCN:-VS3'$He-`^91KMJu0?>+Rd%n@Xm'NP)piA=p"#CsOh5rDuWcT?YYI=8&Xm?;nlht%o8)tbB>F2_Q>#Sln-=XnlkX@"eVM2b^1VWh
-KkE=I\7&M-e$R%9KmF`*!X/8<ZYJ'tVqZOY/..E/f\c68]D_mYWHU8fZ'FkUDgt&55iJh_c_!\e0+?=P8TZGZl37K7M^oLkhdUQW7ec\Mtk7$))o]_]
..R4O1Du`)Z8N6EfB8,NHWFdr9jU&<Wp&=HI??lIl?384eC*,5m[g>$nIKooCp[D7W>a?r$?._bI2QIKl+kko@%'d48>qIRiXfB`nPelUi)1[oVCCm*[
^##O4Kh%*/N(83sW`/o%(dsf20HUIA_NYbb?,NlRUjiLF.BWUR!MODSH.=:n^&LdPooZJ<:<QKu)*5Kue4*-j4p/fgA6ChM](o-33]kn6hq(d&9Q4LYP
jlhXr]n,PBd8unC<QYa=Y\r!]6$*X..02N`)o#ir4(Di9s+p?Hsc9^L&M#ohT1f]T1kTF2!A/*RoeR09KfsGs1%Gf'B\ORj-btJKhTWo:juMLc-+I)#q
tnd,luE!SVKkebf!ObjdjSk?-]felP*a\J^D#J&Lpnl%-@=iec2Bt-3rEaC`:fe\a,\E;kcLL.s<jUL"9cn#J>[*>$ip!&U2VUb.lTj3!WolBTAI3;-i
qE,1i:R(PRniL2[7m!F2sC`?2;Z:O=]AS>u:jB;FqeR@#WOKNS$PQE.m!@<SI#T3(aAP1@FZa*&q2NW9kI\m)q6O7[3?pR\)+=H^l8[8u\u7-SDMn?;f
Np4guPT=%Lt7+6u^I185<Z%]c6Kdr2j,,$a5G\]uu],(r;?iWsOaoi25*r^'!%/(QPFAIA$Eb]&n[opsf_H#r=j%eJ^HVVG>k_aq=iChF4BSjd01&:<B
*aFDkS&I.^nT_^7&(G*](1Zceh708?=h/]MV@lel6=%L>kK1b%/1,]_l"boo6:6>!ZUFp;:G,68S7&`sN;Qn85%U%&OTiYOC^ne:VILE?G=Ab-]uo9LF
b;+Z;)M<_\?+mWXr;g6eRT(27PQ+2D]`&]5Y^8Xp8=A)eM_(/%A)j?5F]c\>\Z>4R!;Ft.r8N6mIAsYF$]kpn$oPA0'bKV7)oJC0h59;TsDm4oB=3GQe
R*>Ynr*ceuE,gIFu?hL0'>W$*VYf`=^Pl.!E$$qC<,Fi5]Ne0kMFJ0.43P+)c0)61A.`Q%o'5cM!;'K*p[;ZA2*@plFumQmY8*;eAq`CDu%;SkYmWCQC
sq[rbTPnC"&tHGh)neR*a_1u.:!V?"nN8T/98o%'kN1LXQt`U:of<9S7=BA0sSk\/^S/@qTV%@Z3u*SHf$]f:E9r.U.QK3XS(Z[X/cq#!!i!!09X[,l-
7VJ<RqnTC#B$E9!*p#^G?=2<]Ii<L7;5g(O#^*>QqKu:"U@'![,`lMd;SF1][!#KWZ/#F)sLVd,0fF_.J5oPO*_noJqFsZ&hj+jdAYU?DLDTF)h@7uS1
JJtW>q3U2r@Vt%0FT(RP3gr-#f[[+0%'&8-aS,g(VLoGe_6nBfUTdig#'LL'9#hT(6L:d5'lG:K,fl'Up:0ODlsP1^9DoZ]\9`PmndshoQ+)G46H!b:Z
D,'J'$#iB43r7TpTI.^*=j![=BMB-Iqht]*8d*Rg\rnTb('.5gT(-U9'SoMFPp7'=@t$g]aR=t&sqGVnS/4),A-?g58%fB^>M>uN*7rmJn8b6qfTm+Ll
/BB!o_1T:Rg%:G,b1GD/&f+1)32fS1$lC+5V\[)@DGF+KGg+m!/FG1jud[9R7uJaWr[lZQS\5o-EA*:<BZ"/6XDbQ&]9gF;L)1=+a*IAX2a-\P=5`L7)
MU&W0;E@0X&M18TLFrEMi-!b!i79[*U__$.IsD[-@fBe`l=+Ll$\,Y][O?m]hHX#@aK#G[tYn7n$>V'l9>FlqkPhWSf5m:!%&qA#D";bbOT*a<Zpj/Vi
b@;l*L?7s(B1+2B",Vb'@98f"\[KS[dm*;/F$]MknLiN%t14e[Q3E`XG4/]<s"E-UuXI-D+ZO=rbQGApaoWsAF2AP57;AHSb[Vfr\Q6\DYbA81@#.fKl
^%%V5jE^?H(B!5f#$nG8?A=8.2DpJUK(g0O5"Z:nW>Ogn5'u@gO29@C,brXj&>+!>ros%H"R[j(;3h.u57FWIDGKEk(O#Pk,g&9IIaIF]15hi@8[)eO$
GY2uiXmQm)oc@!-pm,f)2l"pNEfhhQo<09"[,D?FoYk(pL<(l5QN/1*?:_q=kR5ua&!lfHCCE$.uhH+*S_p1M2I@=ZM"'(C)hhI@=aAZERYI(-T:(C-$
H2"RA1E7f:`g.i<gZ5"65^T<hAQYh/(\$$^%d@P5%m#0Gg&,po)%Tj'9S(GVj<NLDC&%%.N!0%4iT9oV^,1(7"2TTK'Jan>AJN!*3<];)NS%g13fs`"\
CV+ZZe'S:Qtp*_!(K:ER8cpn"1gp1D5/e+@CrHWZ]EZ>QSX#b-pl<uP(PBj%-hS@SthZpOeD[_s\mf?UrW5:mrnNL;cq/?fZENGc[O!W"A3-;W//=r:u
V/V^+N%\"=p1-#J@hq3u":/I^0H8/k?/5_dtHWlF$atiligcH=Eb>G/N.5("fS5F/`8DHdPd[Bcg<\IoQ+X`gRYi(e(_ei%'s6Zu0kJb'P=-DE/Sp\+"
@cqr8r'Tg^d'EiTF6Nt5d%;=uX?!-_a]Q;3+!tNlW!/POXaUlE/k21C!Y3i=XrV-g=AIH*GFgH2/?;h'L2b8^)Y\OM^kc):8Bo0TmLL,9,ZVj^EZ1R85
,nu/W]qcJ3_cd?o9mf*96k9aJ5pN"$5Va2,tLU#3bc@[UA1h)m-0\ioQb@"@AP'\I[H12RAE!,3!3p[TT/XQ1qaHbHtIU7oe3B^3GOJm8.<n.k&*oC%?
"7jRKmtlB&M"'3A:+[L,Z6ph(Q\3jg4'(8Z[]tdsm2+mG;VrXF5M>$5GtQhTp-Vd;fBO7h(A4n<XL4L25=l`#rI/+Pl>Sd*BjYQSHK9\rZt^EXg@2WlQ
P(ZK(mE_A9:#M4[>q,]c$2a.L2jMZQ7aj_Fee,^FoB;oM>X*-ioPPec6]"GrN!K6&J0PQaKL=7]#,iHZ\Mo;(I__e^lOkbe-`Wj"dT.ISC7]6tJt@P,S
7Qp7]<Fel3#G:8QJ75%pU^a'$U'RL3g;bmSJM:""1j,K3m;O7,on4hOk0]Mp#)UYT-6[E4Gf$r,s,?(N41pF`r,e,4T):9Ph6RS!99P;=8/r)OPHT%BK
L[Wk*2YHhHX-l'(1M^>:Ml&tns3u&$n572[G3l4JTp"5]&`uNui8(r`j3O7M5(dbnZ_HYDkC9L>li6;&H\<3pO'l9X#Ki;%'H!eXUdDsep9bR=oBd0Id
chXKfW<?gAl@)JLdo6Q"W@k\9]SeSaW:28CUrC2$F`HO`%,MI#h6$c>;CNfY3t(m3Esk9ZYqA,Q6CO*#.@'GKVmP<C]$%qd55J/rdCL2bhJ%+;WRW(kJ
Iojcs$LF^4g`W?+`UsQV'202D2,2E_A6tfb53S%ph7F>3'iTQ8I\VcaH\]i:,R(OPB=QQ"XSL:b"+S?1\3R.A$i^lP=N#f@]H\Bsh2"3UVs=oB4j?)e0
%:8])@SD('b'`Ys`X0YOQ5D:_!ffDbtCd+dP4a:Gb(PlEsnB^msI;./@&ai&i=f.=N"H)ooZ0K1K"XDP\OilBSm`Gnq+WMg-k>([:QIaE-ecK2!rTT,d
'=5]'reS`W5?M7RA<7#(0f^UTFdsTO(:J)sq':q%J4'6.Q419o#;pVG#9@r)L>89bII!@<Y0d3iEhEePW7u.1sE#YaUmu%QkhR:5G_C0<a`rX&:dE"4E
kH/$.QjI)7*NDiJDl8834M';MqKe9=Jrdb0)'Zu=`/lN]9gWJoN!Cbf0XdK:QX9Xc?H^`kp^Z;`%3A@@%!f4(=1iXQA(:US.ATiQHA1pLY6'(&h,36u6
Qd0V`h-],$Kn3g&p^GmHeq$pmS>1bH.8#i>Sq5[Tb#kud'MXpeYsUTfMn333\e1&?3E=c$A_X!GS?Y]D#j.;faM3J7)Ma3.6NVVAWN/4&*VFQ[b.j_O`
5j,?3AXO:Q0q[;RC?GnZ>CBca0')R6&=OG^QXXi=GM:7)H-S(;rej8(XKq:gU\\1goTP.VME#nhPB.[7?/]p/0R\,a_>".aR-';1$ph"/-0N\X+dqnV-
p`2@09H3';i+$!.PjmrFOM"*sZM+gEhn+=FVqQ^'O_(*ZM2b%``W@f5bYP%IlVBt42`n.7m18NjSA%pI6KP$t+B_,1Le3LI-M^<0*G(HF#1RlYVr"W^b
];b:[dM8R^]L4m%^O?C4KGeU;fIuWd?rZk9*-ooRo'%^E>3.+N3Y05_$V[%JQSocm`.$;_CEp)Tr*Ls9P*g=i)7FHfqB/Vfr`t)<:(5U"MOukR1NW**:
Bi6[miAo[KQq$2[a9<0/j]iK0fQ#$1R'<Lgm/Z=C?R/uN:oR@fH"e7B#t6R?^87"4)u/aU^k$MAAiOo<N+NY2`d7!CkN6SM@Kk*WMI&;tN,_%!g8[=Tp
G$Zd5a(io)0lFG-f=*e`d4qc?'$MRgG^>L.lkl4\ll45g<NgD^*e\:H=C5XEU&7QkPtS_71g1Ubs.-K!!1DXV<J$]bF0m7Z,C;P!WW3#!!HG.'''
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