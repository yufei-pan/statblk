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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 61):
		raise ImportError('multiCMD too old')
except Exception:
	import sys,types,base64,zlib   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
GhUA(CNJ6"P+T^#60g!*?jSW`;t9:,7d^sp8T_3`QR2*GO5ciUE%#-h!XJeKd])lrY?s)Q!@^%>8(D/a&X_hIl0dffoF1F8Spe4bl>J?Ii`fF<%'.#6\
h(Q7jQihIgL8N:f.('ZBmj!XFecg\<O[5mB'!d(Z8O@o`dSu,QW^9P\gYH9rbYZkQK>+Qf4fRPQ;(J^YYbZG2V0I%$\(*P^'^A-W^u*HXn1O%Cc7V[?"
U*N_WJ!-R0)_go<eq[3mH/cRXH5.lZ,.i.N$VEL"pEGehG_67b%sp'75r5bDA/K&nsn"=Io`#:Z&iI5#:#TSfbr.Mh;g!T2-g'0*9apU4E&mpEjcWlNb
eNb_s-E<X[AbF1tJcD%qU#lfmq2o'Z!caY/Ds5KCRU=APM)bOUqu?2.4S?\5R)p:FqaGOmeKrlIHN!/Q+%E;9:]U\!QaVmodfXB\j&9)7>_`QXtQa2Q#
F4pp5O#EX^ZhnrtHho.._nKP`jgL_^LBp7Y(Z;N8*7jGgknXE>EI2:p3OI2Yq=caFe<G^6dL)'Ck`o(9eHosDMH[Y\gkY:XEo^1m7T-"$)?Tl#OIt@qs
3W&U61jORqr_(I.48s8kB@jlLC_e==Iloeb&1%6(>r?AY*1nPG:X>%c`FUhXd^=sBY:?%>(09C\6g4DdqYKFB/G]+Zl,WO&UATRQ2$*];:B$^[p$b?8-
1=%34[4DomL;#SQM33m3Vmji3o8I\Jhr(:<k>p*!g(sM@L+1I]sHakh]KTtnj7a#o[DL.HU2aN>dX<IGb$a,gXa([=p0sMNqp`1;Jcq2cSGcAad\pZ"r
@Hf56dsaY4@:-COK'U`#Vt5bscUmK1>b&m)9r*/n5)UL%DLc#rDZ/7G//(,OS.M+T9E?mg\Pu<Ar"7B$e^\^@Y`VRKlOs:b";+"<O2*#L?kKio?Y,qE2
@Y48?F$F^)h>K!4LIq.pQFXnqSTl0D]o5/%"NA8s[-DLPI<`$],iLlHL7R6QVCkKHJ$hpLm]HP8('XS&!$E+!rs(:22U,(-`d^<,QuVHSPH0"om>3MPL
DF'S;t/Zt>a17udCJ65XWRAsHj=*8^df4?!%2-k&54U*Yt/m-RT^tXj`eDTV>DnT;]3Qr?A<\t=@3AhM>edB&(:AIV4ED^u<AAJrlaP+=\3>ZEj]_.U\
gMVak1IV4RS^jjbDZ"&OU5A##UXcMh7sH8WXu%Vm<NXtL>ms0n5Y%L]IZnob;#bc::B#V@s26WSiPU3mJCCiArWO7on3s&&!_E%!oh_;aFR*R5@I1/@d
,o,B@/TL@5[B%C6*K7pW*5McU.'Vba=d3W[AmuV6q=kj+IiS0IDf0sfIH+1J12Ro$[A#rU>W:V+Fe&0GN]8TGU$VW$65UOZF!M9&;Y4KOf+Oi&MJkm]/
THYI2O\-):#_lAerXX]EPe<XV^K>M\/(41'YuTl/Ve?6Fa>t>t"Q'cur<q5F%^I_*Wmc_`)iM+f2:/7+bMn2"&/QXN</5L+94`)X/MeeS,N#d/+T!s$`
lQ^K0,$KXaXdO<Ut^rUsZqYC`HM@uT![ggc+upXPYk^G6J=/3tu\;!e@E=S2U=Lb*K8!d(`hPcqqU\jaDN,Q!,Sr;:I>\;HKf[qG5Zk;po7O&&+>p%78
H\iUp@KM[Qe\/m]Gi?8:8_D/IH]\;b8/e55rMu+RPlhNLn7!K./)Y.UX6*eXO<.YEP'Al0a?,.Xnp-CA#J_>N7r,?]K7Rp,d*;8r=[K>h5SccQ;Y_Q8O
5\/*n,k3&&>!ci0?DkadM"#74DmB48WKD$89njMH7TfA)e&J`)H%gr/YKVb(?<0a]IS]8f_/.?t!i,!=,sZmJ^e>J:Ai2rIQ*0]X<!sXZ;RL_o46`'c+
ot'GhL\&c)pt1=-0/rm+>%;#65>>l.710_;@K;3>cec/9K.CW'Bse9/^kj7]hXa=f/6qpb>c(J7@JdiXr1Pt5Z<4dcVPckGIbK'NskCAjh-qUf67LH#R
Ar/hY.;%<^XX'o"[[:UiAUOqfY3P8H#dZpI55bB)o;Qg;3X_Uh`(,Z)L5Qc'otI1N:/^AO@i+3=e,r@*e6[S'ccR?bhaQfQGt(il),M=i_B_nR-8GHpU
V!9`W"ogt#F<J!h>pC_N\>T(gTg9tob4@%V[3h?E*KG+*+Qb6e'9Z5%:FKJJ>8'<gu(p$"2u1=SoN9+2@3;q16T6>Dslnj55(Cq22528`u45'A[QmsA.
XL?3H#:SSt_BR^L[@/Ru=%)Er0P.-3kj5p8Z33+hP"mqV)4j8]Ua`!ZS<J`+LdGJ[$rY036[QQm-(^V`Yr4ith7bBbZ]kHVhn6Jg!a`:Ct)Yj)Z".B\#
],uukBH_8?j1gq+5p-X#)Quj*$X!"I<Nl";k@uhgSQ=?RXi,(FpXhUm@?As;/M5!Z"*!#Rr=d*dg:-_EK%sBVKoA0^g6n3QpC4.\%RL?DEg9rk?LUVa=
iG"%4FULHT8g%l^2]V?[Xf^A1s5FuN&]N20i2a,,L47N?,'E?U>roCW9G3XUV-LdUbQPG`oP?3\G$"L.AY/$GBrA*3$J@Y`S\b2e-LdVrK?<F=:?$M.7
&SW=9,h+Oehti%h-jl#\Y3]9CO3<O_9+s&h$!Fqp^lT+(Mf(22B\dMT6B&r+$9R-d_4@-_]sUhOd.c1Eq,[+#qBKmb1td'P*"eJk+mqI1ZMjP-abt&*K
$'*1t98!GMm&UqB7$eHuaQl8T0E4(JSHEl1SL;jDFtV_h?W^eBn0r<O&U5K6hMj3`U;<_/@"FVj!n@nsI#M]'"]TBn:f=@;e8744&Cj<%s4\#c)c@s\@
X#oBRm73I9u4XVfULL61^R#K3*6Bs4.&-7UF8LkfS_i>g:r^"%>?[r[V@FO!d[YF]S5_)Z40Ld>;1JV1DCHY!j.8<`#S&;u@Jnr;1O>XKqC%*(U-A'j[
:g\=@cL3E7#\aL$eR!XUB*V@=-F,+sA_07=U8!Srl3:??7iG-,&!daP&Fj@c?Y0OaQ=dh8@PMo#7=lP988F;i,>k5>jU'/=U25?L@$Y3ER1Q&dGKBrhp
@`N*^tA$aN26UN1OCA_O7Z+MFEH3Rs4Bh5iMY^l<^QYbM,nBERRnRj>3W/=n?gY29m:??&`G$;LelcC&6m&/*K3#V6F61a+(.];Uqn*_Lo[guOsK`6[U
(WZ'!ts>7IKYFKSba4C%(B%6G#m)Pmec3/@\1jJ5#]-h83[1kY'R_'Hp<8c=*bri`O/p0X_^S2?-GmDuV>2A$"_jc=i`1*DW)UkRlq=TU$@;_MD1LE=0
icAX?67;^54Zm1:I'D!j<gQtFFB<VBQooQt4:M-37UEPrL\Lf$kO#(pet5n<J'VEcJRUYo]tJ_3elHFc`QF+a;:5]%(PT$D#]p)5Hq$f>s[6$-L4aLnK
Ql.m"Uj9i328!:kq/aDt$HFZpsR[J31cD'=2O4qc$U%5Nq+-6\RK?Y,W<Z-^.NiFdXkKZWk\JPLO8hl2m9s*R>C=?ELENCcWX5\P6Z"tXHfeQO<Ma7ZA
7I^kr[*$jhU1409%[E<%m!IZknD>@Ac20!8<3ja67]Hh><Xoco*@@2=/r9,!<m1D!,Zu<b9ZSn<"jirG+C_#G(td/CB!B<g2^AanpkC1@bf"NC`s6.m%
S<3kG:OXFG+I$+(UZ22g."Kb#SE,jCBT'pPKVX_*ZZ]V$7%X'NnjF2`WHbPV$25@d`5NRJi,7Q[rfn2fe1fr[Q[rOQYdhhW_3b9eMQNUV/fcJp4l[XKb
Z;fe,&-e6idn1S6hM>]=?UN3_\#:(1s4,!=mIanj&Qp7:WkbE#?Ja7u24SSU\jGc+^;cW@liqf\21%O=]%6`7g@KifD2pP'j5d5ar$e7_Oml@SNY:4*'
NZCUl738_;@(pNP9F("q!:au1hSpi^r`M2jU!STK5UGW[%:@!*$tVG"1]_F8m.nQ63c%_^u7JL#K:gM&+u,qE%CT36iE8/^^(A*B4%6`U4?KmT:]lWH;
<+W?jcO<&I;FFlU'D8%kid-,\<0W%m!aV8ne*qIL6//n@8H'8M)I^tU&7";$;9Z!O=!l5N0+,L@N2u5$Y+?fL<$Gp8W`=e9+_8f"UrckY8AX02O6IYod
[%Xk6!EMF2+f%ThQ__EUce8ur28P4emli];/MmHYeX[2&mP<3%h;Sp?l6c05bPM2]ciTAA(L$LDY91-N57ra9h_o5EG253@IPeRAc*#:lJ[B4C\pronl
u\G"k7*/O-#gtjYg"d<5$b+1XOC3DW>\tm%q2Bu\u)RdThfQ:S3+XE7Y"rb^@1:'2UUc9>Jm/*eb[!YEG3giI;eF3['Of1GDcA24B:O`e$'iJ>,e5,fd
jjQaNLkoog,k-L$b/:?"qs%*NW">Fi?eL-9HMsH>[mN#i7uU.ZC(O:d39,N4:G!lI36m/)9Pi*i9UUj'n^"3<q?#SV;i/,7W"h(s3h'&co74XSLXFEZ;
/VpJ(slf%cf9n5El*nt@,2M\h7793r_u.;.o`s3C!dOL'FJe..(EUc))Z$A.(*"DrkT`$BhM%=nCCoU,#Q_W7>7'XEb8:PV%BGWODq.MQbCQD76`E4bG
H-e1ePb4"#+;\C`)"IWPk#*6tf+Mj:%[:P@Gc=.EDN`gu:LYDDsiJLG0jN0RSb=^Di'cX%!=nb(+5:tG0!4l!`E_2MjY(Yk+B+pt]HiRrl%NZ4]CDX.,
\Y?'o2J\I(dF9cp#bPQq^#H)Td.Rd60W(,b<-$Zl/29m5/C+oPbhR5G2P?S]k,gA0iOsQi%i'0]A@8YF[u[Jc>r6Y\(S*@E%>.Y;c8KeS3MB"VfsCh@!
VL/*j.(TX-I]l6c]1BfcB/+![/\0ZpA+Id''!?ABW-tj)1:KZL)RmKn/'W9IZ6*<3XPiUU,T\iq%'em9qiZ+(sX=-?u6\UOd*lt;Zb2PG*.e.KNWlRXP
8kuiCFL]`BrhKTZL!AbVXKQ[m6VM1^kad-:a;'8>LPMQEQQ31(Xar?s)o()C]@R4,lThZ3g]pT#pK+%i7Y^JC8),EWfedccuEq89ckK<+Kj:6uTm?l'0
K0)DZ`R";rSRRs_UdRqmDHTN;%3>,a;lPKAQ9TJ"&<o9pBAXq@jO286@`(qT#*6TjVU_jHrr*!G4gQ\@:M`mK^]7*/07aqnd8h;l;c$&d3b)k1L1A;XK
6'u:&4jm#<AIJOn+",!S59El&7Huu/_a+\U5<I5X\08EX=ir2Znh%aD0?IMQl7[#8)`'lf[^Cj3Ro(>2?)<Kh.\-ipMa&Ha)%np)eEXp(n\"$s1_VEkT
l16%0hqfgGI\tmgfe.cYS?c/TQ)p]5bcVfF3-25Sa:Y=3,dKo*\EY8W@pfN_=Gpe1_FJ*2Jk:UIPV%kb#X`4+g$BY#Us@fO>K8a0<QuQa8F3`dZBEohK
;#+*()pK:c&$?<hh%>G]&88&R68a3?D/NiV#1g.[>1tfG&TSk`LXEs3LtI`BU'K&WA=B;heJ0*GMb^m/ZJca)[Ub^^eM!BIa?DKQNEhc;9C"[o)0]1q+
Mkj_f3n_O9a:_I-#-)6ORk2S_5o5H,f(a`[s*_LV9U\gp3ap\q_as2YFsnB/js\L<rZ:a4iaPbYm@'P;XNL7=#n)bV@KVT:B4s4Y;jBDCNJ-C^@a'Tma
&N"oRh]`bI`HV#oY\A4ffMl\nM@nT^KK!&C@&=VQP>C")-\UO.+\&8P*X,;5uS'ukZS<ZdKjeZNu0-WS8KpR=3f!>12DB<[";2Us%-Noj)GGCI%`f]1+
']YSLX:SJpgK$!WXdX#uCR-)&uXeSM\72fr?RkqGfDXH7,Zrl(2Qte-o8DcPO"^%d;)Q%B1)>C.d=uo;*[m=J6n]5!#SMfmpgK`(4p7T^f^K5mCD]!FO
hqUPWjN=-KKSO"-3JZE3Zm-?2Y`:lcPO6O'Q;<aZL(:l59%V#TohgsN[(E9XB=A%H+"P[hnB0QYdNr$\6kaFpJD:[4N6L=GMo[[`(WC>A7m\CZ\oMQsJ
7X"PJD:fe9Sr7d"d7ulWg0\?SY3g/UY7nV"G'YqOnR'@;'TkjiGK+@P=Sl@mEpuUk\.mh#th:=$D+U'69U&q/m?-;@tP^2r)LJBXm5B[Ee=M-.V&PK?]
cdI/%"?;,dW_23UT$kWMfIX"-3]5eEB<K3"t8C9qpg7H$KA)'3T=]Mj\l"J.Gc^/95hc%B#7pLi!!AfBt\^np"UXSq+tZb#JYk(B;PD5UF+`oG>9UaDj
kkVo:_]iKI20Jdt<q\DuNmdl;eBG"ci<p@<ruippZ@[sB6eEMe*GnWrs\CGOLPN9/t85@0;]&APO(Yr\tP;]T%XG.,F9akh(Lj"3TZ"/J<=KT9pJ9$`K
C;[kT(eh,UGY(X^V5k^03h5%g)"lj+_##iIO'+?oYd%K-1JB[4-9YT]l0O7%FV2L`09,0Q\&E4q+J8=jkbPh<#3k,FALW.11Nc3HY+?nf#d00%b1HiTu
?[<39#.IT:RebTWQHsmkFhfe"3tJG/5WJ4.X!bdAFLCZq10=Gboig2BLT+h-dXt'K8:S"GnFE><]?bZ9@/cCA(t2K-SO-?[O#2[Br-(\r5<d0+jZ^l\h
YVs2pk4:Glu,%+gQ0H;S@g]<`b/nSFC9k-=Je[@A_dk@#lN?.pc</XMp4?OAqhdZ6T!UA9cERW=2XM5'[.SY6-R,>-AC540@!aAO#\9P2^WI[O7RIg$/
?O<?4Uu('n47q\P?-_nH%O+>2sLd[&a(;Gmnu8Jdr3'4rnPI<:B($!$%-@WU%5RJtHJ<"$E2S60Yu)1F4tfE:.=ZM)-sO<F%pl3&0=^L$ZSK=:/g5*nL
Q8U>n`E6RN>6CV(f8R9#YRgg2^_J_=L'g(=['`fsq&cj=e!o>%Q\?2$r!\MS\#^<K1Aj/O^JRuD4h1/:XHGPU8>g+^ldILA9]<9`-"++:DWWa/hqRs8R
`&dcLMn3hr47CcKlS4cYTp>*n;]?=N*FX`n**rROc[qV2Ts5J`sW]%,;+9+:#[(2K:]YM6J6PP>PEp/=H+Zc!ch(ZV/)B)nLl3aK.?t?FEn9$DMVUna/
3`g0MW/&l%:&?\"PNe3^4^C+^]PCs-:uffi.H[@MgWK2rJM(R&32b$(2oXsIQ]jTUTD1(Ss8KWsp>N+Efr*-gjVuK)VP!D+nS-Jn-CUEE_A(8CoeT\CQ
[SgLUl<"*lXcT8$P#ML)%/<h&%;#:PGZT";^RV4BZ(#.,<q`lORsGu=-H.cIC_"9^8OL>@O<r&N_%%o,ih$NXT.,=6=[GIku*WGf]^5bDOn7]qdEsmJ4
t$u4eo%_%dW2DV[[;SeZh\(6$L<Wh64&HaXGXTW`-1Dd:or*nT/-c2@rQR?M1pGl,Keq&5[TekZ8!kM`>sXqd/LsY'9(gUMn-2eNn+*f`bQ7fK6Z!"#7
teXk3]$ET!FS)c:SeSe85XB<H:!\(6I=[\j74UUF3Yf@aHg^?'+.h'a;\6b^"Y@H^JEGPMMD!5,0hOhgT7a6l?a#O<uHeIC2inGfo7cFj]g8h$-8=eRG
/0]sAP2!7:%Pui!/k?$7epsK?^l$s,U<musC#NgZ3Y1^"rs!$l7TA)>gqe+kpaHmY-m)>,\R%Q%QLXiEIVm(QKP9lJCk>Hk-.$.Po."M@"J7<U/o=&B/
2:F?C$UCGLF-W`DmQ>gP4oP0KAU\4pbCCnf=oG8W#Wg"Urq$,0J,f;:oAo(Iqj7*-mJaJBAtBEjbL4r?i^NV+pW$($'UR\"TCLa*H:KV.9m&da;,SjcU
Y_j3G!t_2qi*`-)jpSCCaE8H-+AAU110hPHE6YbZmu$@5Ie`8#qMA>QnH/7J'[=c^3R<Nc[@#-mR.e7n*:\gMf$$QkDHQM?<i4<\8(OYWV'\QKLaL:IP
iQ97sVQgnu/8B_eEl$!E6G)o7O*#ktG7W?MOilI3@KfRH9e+I$s)/npHbRC7iep[9JZG#lMZ4C8t/8aq$%#I__J8fdU20!!_h%k.66&>h7aKH<SNGOP3
[`X3f_Hl25?S9a!DQi85;^V^5Q;AErt%48(Qq\ZgSeo2VBNkNZY7:@m`6qJ8:ZFYb_i4UQ6$bd"Rdca86P;&geX+=.iN.Mt+cOXFsAEWbM5-:oSQ>gDJ
N+#KL'Vpe4YJESC%fL/aC1p@JmfFe*h?/0u+0/G3<iBZO-/&TTf/k:"&P`<Og57#;0#8P*OA6Xhf'O^A3f)Y,#Al0O3RpN^/cMpb0PEGT1EjRZmmeN.,
h3KQF;2*d'qPj[k&qtTDZS!QZ'8A[/EDlQY#]>7oHMAh;I):8n8IIaaeUgADSf@fjdT?ncEZg:AfukU[A!qj1Sm,<=\HP.t'!iH<["6DuRg4?,A'TWS_
L+-%LO!MU->9)GQH9JIBd:%:Fqc^pnB*@!'PsNeS[rhr\t-50"=Y_o@89`fgJXN,T*nag0)f$/_eO`mJDu+4UZjKcK?7#]NL&`+mS+GF$Ibu2n>9.r/g
2j#ArXo'2XQWUY>'qVh];KP5BVVpk-j0[4aHW_#9j;M7=WBXQRdqq'*L],!__h0+[`7eFKb(7gSasfgrcGWo&'dg]Ls7EjjgPDe$%AF$o`n[MEl+2E\B
h>M;[TjH/8mY_J#R_2YgO=i+d[O<gY%ckm*`U?Llo%r@Z_>ngYl1WnM$_lG,f<H(];m?V.<+#h[j(Y$0XYTW#A'1>3)Z_Ql'G$XAf:_X[)TDP<AU>7.5
>7?ZB$lobmn*0f7absg7O,ujHn\QL#JSj.b_G,hi$oZbfY#WYqoc&)c><7[6fX]gj]^ZhnqaQ%#Mo9APK?;#>,+o,.(VcIVSn!Y%'M_"BYs&:S*MogRH
/Bdr,cRf!"9]rl5,G_l`HsRj52Xa\bCkg2:6K7O[U(%/C3#=60CGCZlE4k-uk@3d;4&\8l]U504AF?H"#\B';29U\;r\cFUdVbNBmshu=QX/+m/1O[FZ
O@'n"t?$S;hQU;()M5$aia]7-fBnCm';4Xl)1g@dQtFX=dUG%4qR$g5D"6&Fs+>:'NCMI=umqSc9'WkgP/&?=@e[o+4L$6VWY*)SqWM`kQn3(<gaDu6r
rUC'0q\Hg5HI9_BH&;Ja$;:Y1etoL=:=,s/%ksUF`=V@n=&p<`-k)D-Zj]';Imb=l'/ne7=m=<2]c^ahPObj7V_C^nZ3\]:_XdQje(p!jgJTQF9TV7:q
*,:IQ/1OQlG)A94A;7eagW3@rcm\+faIE3mMgApAm"]ZOG#j=aWqc<UON6\\]p+m+T!-6_Q5#,gUF#A?0'm%o8!MiJ,-%F!I3X:PifXG6'Ai#iR&44L^
G5N\TZ#kM!89Xj=f3ucg@"hd&Agr\Mi2Hm2bk%hs*T@Fq21-_fVbHuE"!b)M8XmLtU-)/cngP""]B,&MUa^>iMM]j&(]_K0S57Bs5%iC]+n5X6&SALoi
1tN;<3>R;gq;;7tS=kPZNR^tAo6FO\%3EF@"e]#G.D`R^(9-K<Ho`;md%1CM<LBJ=(i%cP"suI:X(jc4*4FL#dk46.Xr;(T3..^3(G5<pn%;?g3P_WBQ
JG4ZQK0sFSU078Y-un`dAJA\J,A@"Dn45qG.nu\7lNHcH^dl``3.$=fLpfsUR?bO;=Lj*/.Q+0>R4-)PbINZ7DDd+HpP^7%Mk!oPbt'.eGP[=F\cN@JB
^IsW0jP(jkQ>Ea]_FuV6B7"`l?__=Z=&$mpKHs]:Ig(QY*SmVh^IXE7!4]\CeFjG[K<U,-A3<3Q(G=n.5S<<[?I<5eQl.GrJ<@TSr]G9*o9s68S\C\J.
D.#NZF`D(/3u40Wem@Lr=oc41psQ/*g3cs-6k1eLX?[sU6I2CIbZOd0%)DJrYYrc9sJAlFQRGB!O(4'H2?"\/V(4),J_-A7B`A]U6p!X!UB7$N%)+r(D
gI*Sa@%pp=U3&jGpDIr!DaqG8erorim3uOOBMDdUeIa>7dC&bgDnK9R<8kMJF.-CRtfEj.-\<pI'8Ou25f+s8k4[D/q["&#Ga\P/"puL,Wme>P8c^m9]
mQRlgB?5S-pFlIeIkHb>]B+H\GA7%@]>*4G$-hGm3YcN$7XkhM`o<!<-G"A#V,jW;7rjg7,hR3LJ[n.437Km*d9u55;ud0'962SNURjHjbDFnN'S'p?r
Yciu]P#(=bfdhe';mm`:>8nWnYcd^2'CI;rgPJ+1L#U9)usV__dqWqEoOF7U5Ll\q`(!=(RK!.Z#E1>]VE1c2Wsa\rpaSd*j_eFH.5):^&jH7N>?\e[m
0HnfI:EgI1kjRf7PYL\K8k=Q*".uNa/-;(2PBL7]6Q.kNok/Qmcq:,@(nNff'ep(ZPjq.lp0j7o)HC#OHB]&&ZU3+=iQi6onSK)qm94Fa;0qRXof)mC:
+`JJ1N"!/Xb'&)bq9EGe_<SKkJ*Z,kJ&WYUhNVr]5K=u3PWRHpZa7&.;p[AM["X)uK'(.Nq%"-tqe!h2:to>Ym.#jLO(iuoaDc/Q^s**FGSPK+iF_aX,
kY*A\IZW*?6BV#4&B$sCSalpSmCidN3B'4*9?GB6NGg@h_dWUr5pIkVMAj<mal-V3jc&&^k+Go\eZ+Yp)*<PdOFJU6,`s_^.[C!L_4'*k<r;4pobWY:#
N8N2/GF?99^iL.^Q]eJ\^4a(c(k">?Z&&lZ#PBdO]V@<"-DGeNB$HlGgXiPN[$p0f[s>N9c!(^`.7#Pfc;?OtP*-OIprW!>!V>1?rT2cmJ<q,?MZQ$.i
?hs"4&p8F)8NF4D!?QXosXK%jMN`no@QoSo7fWp500,Y4Ck\mE:H3tL'0D%oG<kNFpOp237!O9W"q$Lr*2(\Ck&[^'?qJ'bD+%ciP?BYjm4dWfUuH%gh
Rd`4h)FbR!@UUhdUKh]Z2qg*js(59/,:"rr(Ao&)ajj2D,;9_tCI'c<)JG/7q#e?();JYU2@^/NH\+T]alRaBLplY\H<&&tS'JJ+hT9hDj,Va.IQ'\\h
?GK@Zg;9phobSk>))5$<*#4'@K9+a*.qNXe\D1Y(KsX@C@Kr7eVl;?Y3p52CVC6^Fc'VPbXDi39PR?6-94[WIKM0ND]XP#4Qd-3_T6PFE9q3/C(+FVT<
53=uB6fJ_4(CAGs[qb^9*<W!#n@^J`M,6T7%R9%<"#eDcu9h1i"A_hdu5Re)QJS;*'%Ct*oLq[Nr:=3k_lNEn2dj77bql[NV]`-QAoLE2^X]p'j5$MNA
X./^'N[ORK<Ie5gWoRNXosqIeJ;._/\_eET?iH+^H#&/uIGo4JF:Kb/oD[k905o_H4i[Uh"?!m'SuqSFr,r7k.u)8.9S[!WfZs?,j$A5!FschPoe\5ee
_?FgIt..RoKS`Bc3!p4e%_@O;CiN@\Ct32TaZC!I$E_(g*e:#o([SqgqrL^4q:0dE,@(B+*SM.,LNV'O.OIj''E1U6lE_@__[+')mS]kClT<%d66s&B&
rf?1IsD$'5CG"U*F#M7I5rqB$9Q7h!b44R!M,HObSmV%n.3+GN=NHSJN3lM4@`]_d)"0[NMk6,,MVBDo=8Iq%@\#]rN9J<mC`3dpruW$QsnmE_$1a-*h
GBrPFKG_e'A"6m@;>ZcUJuA=CG2*X,Kiq*6^:c*IH"1]cB\;^Z1?TSUJGHF-ei]iHRTljX?KGZ<Q%=Wa]jAD+`'\R\B>B$6!ueGA0^gFs=SiIjmVS;ZX
$k<YuH"si&l^IM^]G,LaV)M/n.Hh#ltNRi6WG0Rp[r,u7[+pA/VO3;XR:4_P2^,?nnJu\h+BRTQ"o!->(-U^oRZ$QV!qm[ucs"&u8g]g`bgUA<_"fh$T
l^QEc3NL@aB.1G\0N/dBcObjjkWD.G&i0:rK$sN9qtb2IMId.=>p&VIL\H-2SbQahku>Ya#SYnec&JO=!]S?V.*Z6uT(#0Ff&4)l5EaB`CbSJEer4BpE
t*tG\9GhL`:Q-"p\?6_8;O7s%Gr`n0Ij@gF-UlqF'aRnkfe;t+*,>,%NA_E85mU\TN%#,#G\,X0hHL.?&mjOKpc[1EU*&F;LIML7j]LCU*lbd2Kp3V$)
C^Tr!0.S8l%_*'YGmi#aFr=Z\DWlZfYtj_PL_j*onA^d@#ri>P(aNOPB@ugJ`kICfp:?qVf2LNke#IJ!U#fpJtF8^`DDYm'U+6P8Q\:q,J_bVNf-EH`7
Vsk,CDp)UJpGMJ_!I1"a@=Z9FU9fK3cE8K5gfZ81&L>Y0d,GFi'l7UffN9sLNB=7[lt2r=K&3]Xqn/P"u9dHrpr;R\_kiAld^4MAF2hBJ_p[D(g<o4<-
1mI:^.)OV*`pfYYbgJ0b9%aMk;(NM;]SnI\,3Z!".P'?iF.RrG[2@?SrPVSY(bI3EHgM6s`A9qCeCK=]'0F--B:'Z`#(s-6&dMD4Njg\Kb0.2[c\S[b`
2PC[HKS=r"Fn9b\%3!VXMUQ\XTI"QLFGn[-_-a;RoU6.+@$F4G<VntV)Ukch1BPd)ma*=1OtmQL*KpHhQE/+0>l[8SHZaPi%qhfJl&"9S_-QKG7P6$gm
kqoQ0e\.\k]$pTd1?NO!P9C$OhSl&Y2<f1E]G0)#e/Ao_*a^CR^H9jm[uDChOn0dgZ)Sp%=m-"bb@`cJ(Xu`MrPeAOP,X/n_Tsp=mtL%_9a\O-I([^H'
6,.O48CTY&Klp^)/fXbj)_H$M$5q15OagJYH5tK`_@hDbW!&_dKco7cUad2bA1JX#ZnO_<dLr*fJ#0Za2&nHVds$^$rfj@JB/nT77AH;KX2aMmjPT.Q5
Z4_-]!*&4$o6(89I5S5U__6%tXL_]]RYj\oOF40GGG=5UY4[$j`</@Ma>*0fSUE119/+I9(;eWSCSJ'd[nTaaN_`TXU*BJ4"n'r00CekdY'loN2uD7&j
cQ3keu["cEV2']'kp#mrC[Z]*%QRuQ*.'of4:^-Il95WSbo'=EdAU6ODVtmO"h@J0*N,8X*'8qOL38&j8!4CYgT)]n<%Vnd[WjW2J>.PtJb<h0]RV0<<
0JEoOR:U\8m$+$O`m[B]P%lRB+67l]D:[&f.KnB+ZFrt_A*JP1gY$'g>bab`$)@*jWMDbb:m\g,d'OW<j:F%^)[kk4k[]S/&hF*88'jR_<9jk/>[6,:`
10k4?SKkj?\E5Ae*,fpXTKO#9].<AC"-\2p12::8_R.&$Ko1oKh&BS6H:!NES=p=>4Gb%A<HsTGC$M>/^+76?--sE0'%Is:Za&PLP%'^Su%)s/HA]bWG
,#KPh#N/G:0fUTmbYG-7\l5@YLnN2/0W"!qsjlJ8;s?kafM6J4!5Q9S*VPYp'm*(_UD[&5h^qd@b_rDh/\eoJXoJ$G54,!/YUt5]DpV_kFIqr^P`M^qh
N<[:EU4N'MQZNsCY"9DV_`WQMfhM.OE(k-M?jpqA0eUpD67[U#I6C:<Z%raC$/kHSeUDTl*;:Oj44^MXnUa9&ioN4rkGqQ3s5R9rU*%l<)IS,:uWIf@R
2lMW/kY6LDS6A7EeoAoW+"TgT<r&8^>F0WF>=Q>YEaWLdf>BAL/IHTl!ntbJd4FG?[$e>','2+6s^8k[,@<UaYmj@:G%M9F$i]3iu0ed7[nmf'INn1Ud
??5\>p0V&'.?"]m\&*u-=s84<Pq*Et8rr^[F2MFteX@OEeWi`G(!nI$Mla>r$4S;eLb-)r*Vre'[TWP$\>;-Q&=L3tMQ^`,\P][\H_>eH9Y7/?,'-a`)
u^Ns@8*")\9`qQ3MD2AHi+O!1(eA`l>d]i>E+41feJDl>(V9fa"1$D;mhZ<UDkC&7Q$eDgh8u6kr7tD(7J$/+MM)6Vo_SQs'(uYWB&"_'=6(l<jVDDaX
KW&:UpqG_*:,I"W)VKm.+<CJ4a%q7Z!ZW3B&N0;JBtee0Oe5NU[LZ^+pJ"#0IF\g<6BaRXYgAIFUS<lbHRZ^6i>?Y<sT\K(8[Ld!Ap+$AJBuKAZ=;3dj
qN6AZI\WBCh*7<;9TLX_\[;oCWK3_"a`'7?R[RhpfG3_S/%.$^o%+ol;`fDn62,4J$+1J!i/i9"sW3;oE7El?6.6HX4e#,/jl]1&ip_fR!ICZrBPCbXE
NDp?RoZksdDkP&4K>>n;C*^<Km*]=g.P'UVs=sTnjr%(V]+.%Ai/a>j+"2rP5jZ>L.hSQgHs379\4`tlrnN1keXZj&tKb81;;[@8Lb,3\"9Z>])kXJNf
?Fm8@F3g=2odP$ga-Q>,Z6BRl&V+:Ks.V3]9iE]!?e:LeKk=nSCl-D/f3pA!_U+^%rDS`]=6[HRg&MO])d_,7<2:2E?YF;Y:IS=Cj.MQ6I#[rBO0)e`H
rG)aJd2;%rM.3B(kr8/M+9$j,JjPKS4!VO/2[#.22I)""O[n+d49`(ljuGHY`b#^UXF\HajoD.c>[GQ%F(0V%iDmq.9p[NKK%e8@qTmn2j;I2)=G.$XS
.G&hLQ&uMZ"bti`[0O^7/R3Y(d35IakKZVmhZmf5.Y6hO\l8@Nuai].Zp#418rm?P;a`%njt*YV/?g]+_#S@t2GO\ZNqiN?$ZF?5<d<S(l_%gWjQ@W+B
m/K.erdEtJT!89HtTh1iFmZ*8na&RsBCKpl<FI'amJ#\she?rgd]oi8WSU;&"V>N^@UF?-HsUTT?46Aj%,"XJ<in9B4c;bRj9&/YQp`d\=XE]qI-]%5'
rd^:^PE>Msuj!4N]CbklrFiAgl')\T6Xb')b.=N+;/'l$i%0E5uT$o/RV%3iHRZstM)7Tn.!#.'>N[8P?-09Yfk(KT#Jk=PBrO6F9nbpf\n`AN_:>_VT
"PNeI)#W[D1.m&C%9.am82S@L7c^EOlL=H6?B@tEK0>7jpHb87rMdDq[N<8eV*?B4]4i(Q36[u9F1f\sdZNGIh`ejSI@<s;*k65`,]9[aUW&Y,]h<;?V
lou+Y.T*l%/'^CHn[WP0f^YC2<H;hEg0I?IkhR'AFm6'5C>^h2_=?9\X2`Xh:k4S+C:2m9'T+\NX,7RC/cF5BW<kZ$?W..U)dRJ"N1tQ_=p+ES`ZuQ(t
)f/?0C-=>6,(B#b&%ZJfEMaD6Pr8>3Urs6LTU(B;;\.'KTHrjD%+N[5feQDiWRb.:@o7N>u79F&S'*>.5##mZa!;SV=r!_E"$4STpr<f?"?M3YF['dGP
#=1TtG;FisQhP6M7Y?9i7mBgCfm4,'^fgu*[-i9D?B896JRpV8=_>cKC:([S2#H@AR-4d_\NQb5R='LTl[Q0/)jj=K[siTlK)5u6J8<gET$9+)//B^ju
R1MNNei<]5f<r+AWM7Cqk#M#_o:ii;,;cnE9E4p5,E6kD;0H;1BjqpE9biW&4O"UH4d/4iE2-L@7hDs6-63Bb:%h9\bMp>\QS`D];V[Xpa@5/Z9q7ptW
%4kG!7bl8-/4iB-`MAi:P?+HHRE5DIbd!'CE&">h]#\2`'S8oTo4eHN;1WGOjIn:KQiqJ>AQ9G)7_b8HWb^E,#s7)!'H9Fah@611k'An=UHpsuL]&;&1
secqp<@3)IH?7&W@b-8RgPRb/Ga#FJUjd8m"!hlo@;P`$gr=l#t8fl!9)\n`[\.=E'Bb?p0X$^QXg:J>LOFLKgb$D_R4YI@qq1[fL:C1FWPOH5FePRpo
-ug+gaYR1T@?JD:H52)>K+Q[(!ceddNB;Eehd)pBFrT$MJ[J?4'j<:GAqRg48iE6.:.fcD#&5IT>V9OfX7YIRjl=4`9Pq5'l1G?m*-i[/g_cB+;Pi$c_
kJ9QeeT@UELS8h\naqj<K!+!4AIO#^a[N0LBde4Y_W.iT`M=EPpO4HTa&fhY_lblSAd3hK8;YhC3kd">A_9;hi4cD+Gb2knn.DI*:0/A18R%"KJH5:Y@
3C\+mW^([tsd&rKK?k>O)jf^9b0ZjQ(,a916cb!;7:/q[:Z<(E8XDkGG):&e5VFTNI!oq38RKU4rgl?!>35-_P4koe,*<p=?l63B2iV:+Y+q)3>W?g-g
=Tud-&f+[aO+]DGjqL9>HS1C-^>Bg[B,0MZMfD3:)\a;F6>#$h_PoX=OW;k[#qO_/O:t?n"DaYf64NP*=';6G9?VS*EfO=^7@MDnR+]W*31cH.c$Gsh[
.Z@rRV7&[Va]"c20QP3Z\P&d#_1GSVKEs,K$ek!L+#H:Fq<a%G;RJ:eiD)TP1@QL2k!b_g9YR5_@Ah&1j`PHNBt`B6_,j%k>#p4c%])Z_goj!hP&?q,/
s%=%sS@_N9e9C'i9,$%&M/f`gD3O'P!:CaR8ibncd_/A&i?[D1a\Fh]/k(e?\2?[@s:22p6j*fBRX:^sSUCr:1uY_5rU"2#gACE`4prZf``NAlc(s9gU
cOqp\.2lc4if*pk(4n+QC8\.]MMEC%$3Y?uBk]2a+tQX(;e;>4lofIILRYbZ5mK^6c.E`N`a@nu)3`'G#ig;7l7D&/!-crJ+L6o6HJKrEsq==+H8?!qD
,53B5`*\FPWb=_@<=^1qUQ6N#AVA5J\e;qc'=.>Ll;r/aS/Coks)*jIH$E-:'KB8)e3k;n[Io?P@erYM@Hsh']Qq]7pXmre$AaL0*gh0B\c?Q't8PPJh
rY<[dc)"[c%bFgh9t]/>bh8bn9"%'-9Wj?uirid[kqe7[PQaUAdGgo^Ha0ChHr,`I_m[$D%hm2ammSh`GTHb!Z9'n&eI$]OmHo9/UY-KpK4TL6;?;d31
-]up_Isn#`XC"nN$*<Ggo]B=Kf]V3jsA`u-+.S9fbtQp79M2*-1rMkc<\Wrn9UJ*7oOO9GSbdT+R]s#>,#QfJ9j_p[b=l(K!1-km4-d1]3E8.`q_!OTF
OR9K%&?U^L@Y;4ZsCdXgU"+m7O7FQe:[tXS(M*VEXM)g]>B)ZU[B$IKP?UQOtf%n`=Ii/0=q]e!kI1N/);eOUF<hq`:!L&^W5Y<uZCX(4,#/jNuoCs)C
*tlcJI:AVt_Si!t(>l9QQgUBLT!.-8cMDglbV?<(L>q)+BV*h%`RcjUJ]Im`JZ$>Ib/@!A1!c3T:@Vf/%:fTNSe%'lIpp6+k6cNg@>VM\MB^#nAT2YXT
%D&g[r(8#&sNbblW/d,"6IC7EoQDkCq:1%SSkDCDc#Ef(D#R#*K5VronFdM00GlmriS)abD&uR*KJ'Q)D!D-%dP4OsKR%<L+l07I"RHY6/f,'uR00s8G
Y%3+Bbp2CR>"#K)$_&2Xdq(fO,]Uq7C$Pt_`4$5R6Q7jk:6,Aum[So_C:(bAq"3AQ0,UV<bnf9V%*s8rB_[@@PDdlq=>kIASHE=#JCX`Zl68tH`bibtP
rr@QM2kHc-/'aE#V$V0`JTt3>(LoMc3JD!UnGGGTOdPF\2-"!4jC_rZ`-(f-S$f!a&ME>H(,I#^AYOPi_ai\Jg*'UmSk3_PPT-E8@P()O6ZK$V7.t@(U
_ht&YsEp_SDU."Bn"Q\MtX%#YrN\1566c9liQl!QDEQ?6mEKjuCN]R#t2b[lM4>BMlYRQU3m3j@he%RZZhnM;d]c.jD!_gV@SEm$5G^GRd,HCKi+dB^B
1]A'_p3]b(+&+$Ig.B2C+@Ta@=E`?b!f%og"HTuTG-Im#q,Wu_j,)"_Ze$9J8^n[IW2[QtWbg!NFoGGJk+'):Z)mDc[El&^5F&r9HR>4#U/K8`36gZ-,
d^aRN'Bf_3S/u*L);kciie=heI79>HXWaSo"D"f#8TaWUh\op]VE+U=OYEQQiZKH9CQ1"=ZJ+2`Yn"1U`^]0u$jPI?VT"N9KXi$WrFU19Sj\4-\M2a8+
I[q?h,/"cX;SKhbCW.VL.'<>8ae6&YiBus2jKR&,W<iFP5MTUkk/3<`QL:*4hJT?n7m?T<2u6J&4IHeFe%J],SAc8Q*:D!o@$URhb>&2*n_nF;)[Oisf
HC.$6*3&GG$K_RJQF'Y?nuX[ZBCLrk3#g?bnfeg6<W?&d2$;V\'[RT!N4TYS-'Wq/,m&-fr!D\Q2>R46=h-=-?K3(c7L<0!jF[[)?n+FFNbQ@)U61KpW
eTMYSWGdl:ncM$pYBVX*eXF7G@%8:R?Hq_7Z_]g=VZb=\foN.$6g$e":(gdjHK]b=i'\H=+Jkl\hia3*[9s?1sPXXDe/SEM[WRX<uo9SApTHR4D[cQ)!
^"dm(M)'Hak#<:P()<UbS^p/P&I%3B0-6JD0m<WL_RC9-<%qkrp`S1PP?2KMZ8lfFMYW0EBT1hhd(-JJi%:EPKR&p]!@&D2ICm7O?oTnu.-X^Y^umkD$
ieFHE(">.'Sr0/lmBqMf=2!$WlBJin(@P=OgRY<1#^5\q!.`Tg\q,RSjMk(:[6Aa-,84;oXamR*!ON!nr7u.H%EL.(P'OA<R9#e#mA7AAt1do<cF,9p'
Q`Mo3A=jcc.;UEedO&o]L:IEA@(/F6S<T_Ce?8*g;9An.og)*Q.%=5@B*P;Cp-;dpe:mTb=H<n@SFs)oLA_FE6o];44i^UHLhS4j$Ds0Z%jddr]Iegng
Yk8YP>XQDjL\G\rnM?A/'7[_mZ/VcPeCJZVd*:Y9;+!*%\V%<-)u1o2'6%*"IE4?hCu!,PF@Qm@V]$&ZF<Cd,TF=rGI%pW=32SS.7YhaMk8)2<F2J.(l
sG`@K\8lgj$HikD"o+DoSY;X*L!&>p4;L+K3eRpa_BS*f[3OP-uT#6=Yp>W+WV>[D5VlAo1\sXJZ`ZV=RN1[mq=351;,=kHhPc-u_[QJRgQYD$2T`2/k
Bl[Ml[=>!ARm),+@qJnSi0'2!(#3`bYd1^$p[K-[B3B3VeZSrSO.E!@UV"O*]q11ZEeSa!+n:CR2/:jGb[=J=`+DP%NsDpQE*06tD;h'[`9K<[uPZdF#
DQ>`:b,ck.A=Wp3jFWGqg^V'"rq/.mX4k-KFUl/>_,cmS`+OlADCm#1YiIG%S[E'WWl%L#Q@.T5c+ALZ;^mHo^UX8o<RX@j,RJSIcHEq-i#5Ua7Oi3oB
JdWW#19^,uCr%Tli?p.PG:)RH0Zf3kF?Ui-,Xm@lbBHFR!gk3"c1o)4K$+1X)hd)%nU`g1HRDINQOf+J5J-qnLb]rGqrmH?Z'FmW@"VZBcg*sDGdnnq#
Qr+EoG'JY663-C25;/@&'VCN*mFb-#AGdr6gm_(__NVd9O[]3c^*Jq[71t:Z\M8k0jls]7cap[m%tn<"?f.p4$G+MPjOnb2:hMUe+O+C,7T\ina$7u=a
eZm-B$/>VbR:#I;;5Fff-a!`Mp[:9<htP'C&a2)0^3u<nGR?.Z)jI"9,$R`WO]Sd/"Q=(-@=B]&o$eE'!ogn3D0.4?JTl[u8ZJ(bDK`8>:8?h4YR6^)7
+-/aXDDJAt4trK`)-h0\u@s8BVY5<NmUZ,3@D'gQuEKtK_eq%+I^O-2jCGrEM&_kZ!*$A(R9e%3P9L<q$;qE#d(9])QFq0"M&#uae84B*CdI^0\[3jX"
p#^W"Lon3g60p+N=T3@Hl;ps6n*?C4<P;fRF'+qu%#_2sRS-(R\):9&cG(TDo9docf<&Z.+PrMs!(0Mb/%tPu4#ZkB=,5jHU7&\6Ha?>b@QA[&<XjO0c
^:kEiKeiAOD!d*K:?;\58[/7Bd%;KASkO_4dHPJ!Q28ST4@o$b$TZ(Ec"T3Ziek(C[AHhUMstUVG.'AQKg2:@*%03BKdQZ$.%]F@`!a3r^$TSQqIa#f?
0g2;5Xl>0XdJ9b@QRq=UW`7[QVbd;a?08GCPkpORStI94X6.n`O%5M9a76210T).-[;<u6''bT_q[t(_#7qI%,cc#C/U.lR,VX]ah2$Z)TO*s/Z3FY,M
Ob-40ZWUg5-pi5Z_G$$P,*Pb!T[:"9`41E%5V6l3oJP+gWDRjA8!l^F.]c8ZMgpLPd[FLO?W3,mFf>Mi26pAaAQLBQ`tFku1Cln)&Kb@#Yd"1n\c9REh
ttNFf@jC"Wlb:\o]l(H#hi'5l`M=(A^ORC!uJ,SilY,gF9bcfcu@KOVDh+f)Jph2+fgLk.Q-^inPKhQp[RHc!Z\8mUfN*-!XoQ!6*/?+J]5#YG5hp>J;
iGYBR!7K8Uk-cIpJ[LNqW4T^=aFN.ZJh7I^OCu2bO7EsbOYZM5BnX@&o8GU5\U*uDaG]#Im-q&$aT+8$Qa4Z/NpNg/VB+;Ch1$p)?M85!]98nh%oc?,Y
m$i7sM6:R[h034Ls5sk(2@jFMdTgL<Vj!$;b'$lb1b8J]AW([:^sq_&cY$YSCsQkcft7(>F#3-)Z7D7l[1?2&;N]UFM4<LB91WeoAUmB+2Q]e?d\jLE$
jqD-9&KG6N$YGo9H5Y"ag;j$Lsk7\V:n>#niBN:4JS2l)ao[oml&JG@V=Gc<A`*g?AIC]]!Ng)e,K:;Z!N_H]=a^tG5(1SH),SXl%G'8l,gPLl1/"o+,
/ZF2ZH61r=p)p>OG_neiE%TYr`]!\3d)<!ns"7BKh,aH?^u4N_--IN,pJM"Ch==#2c-k./Zp7_#<<DF?.BP+e5pVE6;c>p50fjUWuIsXG^s3m3eR6jMl
iRE4j+r(WG-mq8,mZQ`ht#=1O;imIJ+Tj%MnNRA;G-ioG8%B0Gr_j3@*S,m)S\-?PaoH`=4%+%Yi4a=!&Rh;CN*Nd]MR3qWG!)D5q5W)S(+pZQ.CZ^"F
;10ZI@fQNkhWWT(HOq>LP3JGuCkMajX(A%N[IB@jZP0CPIi&R29OsT:A5fdg@g:%uUX`c@aTCucSFY]HN]6$)*W0&Hubss!hTjTuK+<\Cgj-*Fl[R5rN
1K^`UQ=&aF0U?mpGt(EO8E9kA#]P)(9Xs.%k\-?$R?4U^h@-P\QP4(NL!kKD"eV%F%3rk5k>kR,<SiPA:9\"&H9UAlL@Wa3ek3DF(PEr15iCE,@&YJlE
BqH:P1]JA4Q?XKP?/<P/qO,YbR-G/%Qei]d[<la/"$C[4[;?26;fH>I6l-GArDhI-`8>eIV!ce&d,YnpKgB!S!@N),sX!]),/fUH`*,pa-5TgXuEeJQR
;,!U_r37N2M+ZKC;FWe6ZXRq:Df3SS!2W>OOuEFnk^#oUi_"d;2;8rHXH_fkVtu3__!b\'9F$anSn1BNaa=0m7P1_?O3Fp;&i;AC%.BM1J`A$hP,DT:Y
&!bgFd&Ab3CGr.hhR6RTG?gL(!0Gi(CWhAf"]r_R1oonu[sifHU]56B>iL+`m;4JK;=,9Y!PABQVN1.VY_s!oj$AUmJDWB8,(9YP+/3O^]A=qM"WB0Zq
e1rfsF7]1`Xhbse`BDp:__+k%a/_5K09YEoLBo&T\#0;)EMRCCOKH4%a;Q_oMAu!2a+>eN)+VBnQYn]O!0+\!m0AOj6l#P#l:+uDUj"_-8VhWfZc,&K^
.aQaS,&O`Y$XXIpKqad$*orZRDF%A@:q"F"6]hItf9MuibNp"4B'qjn*$qs?K5j8t:8VkSf^mj;mLtp*BjQVc*S5375^'K^n,2R?E%?6mBog#HF<AY>j
>Xeq<p@SA@TIA*@WRgQp(8M;]#H6Sq^^!$\a'KQ`",5g*5/G#S8$6j)kqj!UQ3Qb!pFY@)I"@b8Y!J0r*[/+$.$eHR#>a6f\f*.9[5<U.msnWf'Y"6!V
G#A"]lKda)R??TnPo::Sb9T9Ge3'3ttPq#I#n@!mCR\-3*N%Ggsg-_FN_mC@!.BP<(,`Yqj58Ya#u&\Q.!`$q1BZgsWGF&d6h'W/H(%PUD.+RDZ\26O!
Ih3L*\/Q*c6[]%FM2!)gOoeJ0D)D6Ff7:#?#\BdS-BRJ-Gu55GH$%d(QLYL8'QZu'hgk5D<-\P:0g8D:&#--%82&c'\.=VT2"Z4H#ESXd:((MQO<mMtV
OkK50:@9:Gl4d8I%</npF+1,Gk46:Wj/8M-r#hM<gE"(Z#^-aAFlEtC%3(k;+j*9R$9]7&G8..g#Rk.X(;lCB1NoSl>3)M;MJPS@*%R!pd7Q;$j-+8*.
NG/mPg@G7Qnl-Y'fu"s@2%(W$`><@TL?s.5^\sLk+Ss12V$E`)5/[G$]NRLW$>E%a4jbSfECsl[q4aA^F5r-4]4X=q?Q>^3US"mbk>&'n,MuMZKt2k:/
O2*Z!.dS1iZX^KO09rI!`hjl!6+=jFJZNb=%Nqk]h"+XEe<!n$=9TmKI_-oeu5AudX0o>J5Nh@1,dJCU+GJj`n]t'.fa#&1+6$/jdi'<nV!$FLFP_2VS
bH\(RPH^P)AH4,!CUUNR?]!Q>C"gL]5C;9TU+-f<W'VZ(L"T5p')Kjo<S*aZB40(qalZ)T^lXD?4!tM0Mc"q;Gp@iQjJoYR1pfJ_%NgN3#o(3UXXgf'[
.0qH\?%n&DcIq<QYOarK=Te)C?@R&o2]Mu)>MVL=$k?j>VG"e3']BQ?_C"9LINHAqZaUPEu#cF[@V5-LC`XD`\,l6aqJb_P%b8r]3:@=p5I=rpr(Q`F.
?F^n/i,u'mo.[!Y<9\M,g'M<gri+:N@/m6^]3/W(e>hWlYNjB_aH'VX>q.DXr+8/GGI*9&cih2a9H`.:mpA8S6:C!(;qZ5T!+T)^,6e&a)TcB,+UK11p
cQQhD2G^?LFJrg1OWcDpjsC-6RZ!C?$:F(U1ZmDs#Ih,cXb^H!4<"a5,S)J^3g<qD`i36_A4M8=VH'^7L0CQ'j7]tK<^j*XB+KK9A.ibFd:mt+qc^`XH
"B^b3#R]`]2)ii#I"[a*Oi\;pE\QIX;TaIGQ-RolUt>[BpYPIo>)<;N:D[4-Z#T!$8oF#GYr0:Q8P<.%*OhAh)#KLT;P,i\%ie?41USk=*W_<^2sQ54I
Ib?.!h1,MhDuNa;K94kObo3R[u(M[ALZS]R'MRkg>HPT=t.oRPh<qc$Tcr1J*f1_r3YY[`G<-EoP^4DW4E7f[WhiI8YnP1*.jp`VFO/)J^Ss<AFCp0FU
EIcYJ:pS&qe0J%\*Ag$%pA0L6k9l"eT,K;.QMpZWp>*XSnpkj8p&i%0ZSUn\%UPg"1E_MaQX42.%d;h)LubYKpIK`:tZ5PN%(Z"l'B/^E[9qclW,QY^4
Tf?oHf=mn;hs0s=iCr.O=TNU'tE<"b:XI<:e2-_)W4^Vt^Rrp[$lXYBEUX%mZ?@Nj[[m?ISJZ:*eaC0ZT@HRsbQCk"O35)"E6t`T[I3OUh*a*<Pq41?6
Q;$_-2n\)rUS>%?pqA'MSg4&;j:Qg$#_cj^Yhj_>VdU+)COTX\VZGF4bM;?D]OuSC)r@L^A)5DLFe4DtAOS]t.rt7?rLZ<es5sp]s5h/qJ,Sm90-B'Ng
P>NQrUBgD9m\j4is+FeD3Ssh-)bP)J"'3gaJFYgWIVn`f+8\P_o?Oq+S7H#?ZmD_5/7Lq/9kaHRgmhI\'An\=Dt/P!'F(7%SY3uKp^gIA'WiuI(<'D.P
_PHcH5/'JOBS1._r-bHNI2teHijNCRYFCN9`dg!kBC\%.<2YY?VMM*VIH#bAj/;Ou+)>NtcZ6X3?N67@'1],oY"\B+$9)m_iSQjIMF)\HnBfLikqpP(T
:5Zis%\jGb3ee'Gf]i*@T5j,1FUF'u90X#b*3HfjW.Z&Gk(5=[9J&60jnlhpg`1Pu^0-\:2(aS9kTWAj;&'mU?[TUc&+_YWg=/p;.2.hJ%8#]_:bWS;2
Z*/^$/C*)6m1;40NXj9PQ,5;8SXVue*0pd7;gb]Lr7RK"/K.+r#8Dq2&_<"ag"'[[Ypo3%Bp(Mtd7Og?s6M*N%6)OtW:BUX6:'>b[[8&sbj^.d^[iPWU
6M&jA\>4:#ar_(oKRquImlqR4*\8,52.1T>Pg`;5ZH.hrFpF8G"mBLETQ/OR,1C;^MB7bk2+SAXJ^=3AFSUsod1dhp+_]p]n#GRi_b5<#]=dY-0,Q3q?
a;P9NISl`Weg]-A8ItNl:0VMgB:_[c)j</0XK4*].epOG0.G(T#.<N)QE4p_aJhm\XnF3faLa%&*rmhe*]!$XOXE(D^`!L\:4qUns(q41GNfAek4/?aU
Su*B!NA4=d\Pf@V-t!Q'd-E^.QU&-MohY=!mh3g)IDj=F3:t_?W!rj(=R977<b,SrYplU0dRT@bupa.kU[ubD\fc\Q.c5KCicJd\3;Md`WP\:$ogMO?/
C<3BJ?l<OK&Noi;b?Df/eLFsW>F&Ll<#O6)[G9u+)PWklnSoouXCYIgn=OD3K\@_C<pAnqP4nR['12r!uZEa^bVDd=kL^On,m@:l+JT,X2D"Fk<$jq[g
)Q'iHXkGufhJ3RCRjsTrqgW]ToaK/YY9>p3m:8!FNfD2s?TmRHdB03iP<fRF9TTbkdXB.SlSOjVSFR.Wu7Bka/9JHG%db6Q0*Yf3Ca2C@)&b1Br4T?58
nH2<^X[L2YjgA-Sg.m(D/An5])BGLCH?jCS4c4('1RS[\_VTM,IflP2X^_'''
	exec(zlib.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.61'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-11-11'

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

def get_macos_diskutil_info(timeout=0):
	"""
	Build map: /dev/diskXsY -> info from `diskutil info -all`.
	Only used on macOS. timeout: seconds without output before diskutil is stopped (0: no limit).
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

def parseMount(timeout=0):
	"""Map device -> [MountEntry]. timeout: seconds macOS's `mount` may go without output (0: no limit)."""
	mount_table = defaultdict(list)
	def add(parsed):
		# Skip autofs triggers: stat-ing them mounts the target (df skips them
		# too); the real filesystem shows up as its own entry once mounted.
		if parsed and parsed[1].FSTYPE != 'autofs':
			device_name, entry = parsed
			mount_table[device_name].append(entry)
	if IS_DARWIN:
		rtn = multiCMD.run_command('mount', timeout=timeout, quiet=True)
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
	# None (the default for library callers) means no limit, as 0 does; multiCMD takes only a number.
	timeout = timeout or 0
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
		macos_info = get_macos_diskutil_info(timeout=timeout)
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
	mount_table = parseMount(timeout)
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
		lsblk_result.thread.join(_remaining(deadline))
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
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2; 0: no limit)", default=2, type=float)
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