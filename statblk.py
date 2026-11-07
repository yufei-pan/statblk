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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 58):
		raise ImportError('multiCMD too old')
except Exception:
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE$ig8-O-i5'i9DjZ(gR+RLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%NdN`;%MLm
ps(uYZLt9N^(d>j;?gF2fq.JS8E^d=!D`Sq$Gt&.k_&Jr(6<fc-."_L#%?6QoJ:i3GQHb>?A/=XqGZdH'Nu>j"g6i-cqUX1Al)9;U'hMS[PsbB-tdCiI
VVRN65*?GL<kIO7Z7/-AG(/KNr5CflUSB48`AZQ<O!o56.5)A@KI42W!FK_W9I:Z*Pcu"q#26B[j5r\YtMNh3f/mh[:>.a?bbDGIl?<"5%j?DIG5d/Ts
'(PMF=5S;i-6>tYJB5\%lM:6R^S$?hO50i#I^("oAY)i;aaQ7OYBV/cti8u"ChJ,38fE9?;!dUO&>(t9<Ak)MrFI>U7WU'7u<"0V*sN=aLl+*[XMP=5`
JC1<`.kA`+.R+@c88R'7#?+L\n3"39^b6hl5C1UNZ0Fd`^MNIq?0k8c#hQ/Hsl1^D"LbQs[P+4WE`o0Pc2Rm2\bi3?-,]s37h(ct]?*[4J)5+H+nn;7L
;YJru3S\[3Df]`dbC`NqS9rOQ/t6m5UKh6LE>n5'KkMotdIMC">4ml;BXhH>bce81>'GX:Xtbt#&B)SPT>Yue:a3Ag('$-_0=`r<DT;!F-JosiL\Q`So
*5hR-aXjSc!_Tk7PH$&e^P)"XBkERKjZI/O*NLbXR-_occ*pIXXrGd\d]#rbLu,R=fk?J_Ch)@)[-i,^1Q&R>nQ"!DQ\pS!<Z<d-q\F5O@iJ>S#qH"4B
DKLn9=l!Y(3)U^NH<1[AU.*-)Zu&87MG)\L=f+:^>c*Nbpb'Igd/<\Pufi5hV<0.VcYYis&5IEKYrlZptI"q'TFj=ZN,H"U1gLeOLLlJT2m/_l7mR"/,
3QmpoKLmkjYpSB!T_Omafd/\BOP!IaiYcOF_?&uo$4K-*sK]gi,GEW%cCVVq0#'ZqX_Mp@;:#/rfToMn4&D&Fc37W1SqV%`[Ol,[GcN=E^5HL/=RR,Dd
OMpHL_PJ]hImU*366mj>b>67"Y!L9)/r)uppSu4]k6R[Q`lUm)A(u>%eZ/M9d]W)P%QZmF/=2-&>9q7i(7S2br_h'a<%G<,QRYFoY*YY%4J+h\gm6!TC
N6KFKCqOP+/^r/$`AR?kgf*cenOHl^M9WK3V?bQ-=A)DP]Y$3%#'"/Bk#A'(?0o8;"M)<+*U^i`NEir5/7#^7m96@sLcmciZ<09cObb5+eJZt0(.4k6;
R]hEOWFde>^63]cs!@XK_8kX!^*>"Ac][m4q-.ZNM.`J(1tZDQ@MNu&.P!*p]%]4<X:4=&JC1A./-_/g`VrQb6m!jamsdfd?ukZK'G(g1T:.t=<I5D#<
dLO9Qc)=/jj5?W=0V6j%BV<.a<ipihYknjF'%uc"J@TX/D:OXU`4M*-AVX#N'$&H/?DBs77mf\(]/hWJdLP.LbHnV^]T:?Keh5,7]'jF,_nkMN--<e5%
"M:=.U8CVChL&cKaXT0p5#Y-Fd7m7Y6V&k-keK0__mN%N8k,k\oi[joGg8K#ZER@,Eqqb-BqCU!<'(A3Q'Qt09;RN((!AFli&+k)=P]<:d_)o_<SYLc-
.isdir\n0O3@#SsL'^@uilMEUkYqJS*5/XIK+AtH$e=%i48Bg[;@MM^O[,1\Zb5bN9T\fh?-d'9oXoNGrn'fCu"Y]iK$rnM=lJnNB5F%$(r#4tdBnfI3
ch$gD'7C!,+M]=!r-:^^U0+ThZ)tVUNnZ<I!kVeGi4&ogk-c4[9+.<C#ORbak^O:XK^R!g8$OsX*+1DimS"mo/\AQ0run]Tg-DVdOh=B:.-m9<=&hBX.
PZ\0?l:j?S*eri;:L\lVK$RMmYbrW;qTl_aGlZ.CcdH0mYA1>X-&=O1#',pis].a'4.PM*\-P<8.1eeo!H/`Nu]OEgA(?L%&m69=_Tp>6[!E/htsrR/L
QdMgsb+V=YC+i)PhVco92nVh('@-!YY,AHc6os@G(L3Of>.c)OBGU;X#&7>l,*pc&m*=WkAj*NsuVSb2OrJ2a!Q)<^Uo+kG<LgAes*G!Ym]VfDG2b(th
hd4IlQ&NjX;,(*ik<#u>gWNj2uGrV<0f\)J;:!J5l"N1j<Vlf*5,qW-r%it>[>D%icns47AFHK,biT(poe!Ef/8n!1i7ZlPnU[W#ts'<r_H`ng"jVk$Q
@Q^=\\pP>CZ]KY%^B`lFge['7[2,(&g?P9V6Imh.&;uZ`?#CgYFrOcDcb!1o5=R`'?&n;elQL("A+X$@j_+$DfE=-q[T(S,G*hMhK0/Q1G*hDW)A-4J>
.$0<brl\gD6(<paV4N-L2PDOW?R1!R?6mST_Yb_ZjI#2!Yn@9+BF;J]nFRWWe>+8\>*ssg_[6<,9s86g;5S1lhsRq+'WM%oGkc<U'=%^0P1Vdj->j@-b
fd$U,CpUIg&Vg_##Tjn>.4sKC)<YZdscb8D^R8RN<.<5_f7&!QVkg93<YC.i$h+hNX;9p.j-'s>>f-t\ZuK[PeVQmbdB*pce8S=4%NKq4h.fgU)%E(3-
nhH8`<R1b9>s0nlRI8B@qKnrg!,/CR_pCB4PX1SkPXEfJ^8&omkA1H)=@64XLt2C0r]f<Sao5ZWF^lL^nU8A3245P\I6m\k"0`hrjNJo5V2sC%j=c8-L
ftTe?RUYUHt4NGo:.c$'2aP@i%W'bl[PYLJ3=oJh:s=i,q.Xu0nt@2#cp-[m_qN6QHeA;-FF>TJNe?mBpX:)aF-V)tRY)oG0`IH'.q$^d\FQ_D(l),>2
BA%l=<Hb^3*:d,Lr(Js`V[N8_Eo(42,rXF>a4X+j)8>eS_&J!oUb<#r-7_Y2Yo75Ah;I6(H:sHjS'<];Yb=1>[0%1@<id_-4<G1cuDsmMoeYZV$kBMJ'
G:rD9D_!:jqY9TYa;@*E(B(laX%)iDa-S<dF:dqJdi]+81_G(a^j4`'9@Pk6?X#Oc/kFqJ$m#Ji0_-&W-oe<t=Lgr[gg;qpf,/6-Vq/YOVb[TK"EBbis
#.jX0!%U3[!P:"+0)MHTWsH#6BOVOl;>n1rMcF<W[Y0]#E_J/Zo.b#S%K8E:\iE7?L*[9VInqK-ZdmiehRD8`&H[:d=EocJM>CcrsZ?8k0%Z@!.$/<PT
qrgM_i-HF7+0-L,/8YL\][#Q<%CDCp[F*+QV!>9n,jSk;c<6R&Nkr7>e7]fJ!c<@G.6')o?4U0RQhfcTIj*Z,["r\(Q3cA`U+_gutpO98MC]ag&a_e8K
T9]$jtFQ7Ed3l@3`r_WPkF\jj<hMB\hGBgC:^T/9IWZVc8%XG@J*D"ah<V)f8O00[FRO%&ut"NO/72M:HUR;kJV!t!JlTJD>(@="@i?_)"XAtD;X;KRT
>7sBa(+:mR4nPfF]S44=.Qq'e*bP@ng3(%ZaYQdMk-C?SK+ZmP"h(4c!D0eM7#ZIaf28"OKl'i@1]ik)[H25l+-E!Z&UO(_I5=/QTCUKhR#3H#Nm9$r_
+rk>U.QF02Sq.B6.^<N84'B7#m#p`HEh-oq6&pcUUg&:%'54^WBG)g4R5F"qN%HRd[LFm):u\eT'IEI?p?.Bh'&A2c`DU/%MkfGaEi]0,E.Y2Or3(YEg
Vh\EYbKMk8cqIs7=ZJ7_(@d>^(n"]Z<KKCG^Ep*c5:&YPJ#S*o-cZACgL+\^Qg..apRV7BjF$QP\#(8f$<(iK9YmY8n=,"rFkBY=06;Dfl9+LF%En's#
N,CF)A[$mM:`F)pAq2qrq7Tr!.#k)d1gsBm\P:)Wi!Te=R<mW1']2hIIYi2-Zh9!d[CL_mr'fSPa$5^0EMCjbQ-gr^FH2^Y96B4"/]VB.Y[K2I9l&B3U
0jTnSfZFUW`O3p(_'pms,;Pr'(_d=U<d6ZB9cRKd&qF#^X<;]GdCZU"_=6rDHK6c9I*B`5@@k1#%:5N4m@K=]8,N%5Mq`Erb`Js[dA,r0dhjt*:=-mB?
3d!f`+4g>n;VRO]ZK8<9U:;:$Kj5Bs'7%l<Gg=_bJYY%s`ri;G>Wh/^hLBn@]AB-uV;ML;2o,ain&ENdRFq)[M5&u22bc&Y===L2cH0"0L\CXsd;Ga3A
r(-@Bm>&RF*L"nRB)"/L2NO>Y=7u55?^3[qceCn[!3]Do63`s3g5r4@C#sAo?9fN&Cubbts3qP5?5W#\I.3>X^MO-Ve1_h41%E=[G[$T)piq\;^!PVI+
pOj0F#PonUSWJ9Ep/:I5nM^E4!=SrpA3[uKKt&W'fD=nDCpEaFdbgqpg,Z!.%<6r8f:3H[Z3[7j'<,2^u%=h4V#'d8(V+DFB2KOJo-RiK[>"rhQgrS/Z
m,(*KWV*WHYo4NWbr:^f.o-:e8\V8LT<eB@f9#T\I('"]GPVeRAE\`aTeD?p0I\mptdQ"L(!?PAcNaT!47Qpk1nEFp#i.lFQ]/oW8ZtE^`N3g=E]C4O/
ob^l\`Z9@3&mD/^j@I*NjejFWFlQ,C8g-F$T:Mu)H@o*n[cB7c3cDl]::K,D9[kntIX(]\.W%!;@.8W=WV)!t#T-;D,Urhb,EUZ861\M;_mf6`TO3un$
W.je,/)M:VAUrFO0.^[C-U49`Riu[rtbNTpum^?>k,a",m8QUt;(A+ShgojT+XZ%k]BSn6ETjg!<Y/-ZucW.bq3^jIB#BG3-+<Gn`-7"RP#=esu&D!Y-
<tbeZ1O.;X0gMs''U:u:8tT-a.=/5KoF%ZQd$#C8[e4saQ$R)r\&j5!bRCA39.LcZRj(E;duP\Q:RIFg#b<du"_;9ZI=gs6FIE])jj9qq"idOKTgg`V9
7^EO8T@U8eM(&Z4VDkr@/eNb"K>Khrhj.5>Q3+?%E9P'UZ#F*efiUD3i_B58;+f>Y4#,5M]6\uRH2H:'2U(d1J>CfDeP&1/<g:]0UUSM)eW4f/&LAM1i
#+?#d*dK!t:hg2pd/FbL7YWG9$@gf-[a\:oZbL>G3/4.R.tcf0:or3EQmP;?iFoT;rTH?*7J>DKA"4D5\L/TopKkHQ&6#j)+R(-Z)2J98?g1$A?!d4*4
/jmbu!'R4t/P,JkjE#U;iQjE+i*h4fsFT$p2`[1J28::5RGWCsOiiXiMLbt:%f65t$^r&^"qbB)W$dMl66Da!nS3'm^E!nfN-f9Kj"BKl9CW#p5](^uH
Qkj8c[Z'u.I++f<SXjZoi#;8LS)g,KLi8'R*Fua<i^0'OmF+NJ-hig'pG'R?'IllJS_s8S+]&(ink.4cb`^dH.N9KuV=4A&fRJ5?hl?2NIbbj(mkRpDY
W>MN8jGrk]Hbg*s0e)a3'ZBNMqZ_:]]s;F'_>;bA+(MNfQ!(6^\%k!+o7iG4pMJ`bP6BKfJmU!Q%T`#Gb,LnQD`N;^M;KRU@-&PB-9<'Ei8hs(kH*uH%
bN.Rl\`W6*F],*).h_gE"NYglk;3X'q+#+F`r(q=\7=+aM8km@f83"a$*bQ<sM@Z,-uV?H9BWE=J%sUGn;c)Rs]>LL$u/_\UpktpD$OUl6;VIYFTU?+1
c!b5MC#qnZRMM@#c][GrVk:]OJQtGR:lC&mEBX+rqesegZA`aP(-+F0l<ff1,)+,+_O!cS3t<T?hj#Fr+dOQ,J+tqhKD\601Ece.rE@-h%unVDY+k[N=
W,2<r(^?CY>87A[nK"NVW3E8;'4RtE2js5qKe9tE@doJ!C1d1hY!]=Kc/#u!LR\S8Z#G'A:OGN@2QgfB.0].n#cnu3Lqa'D;e`$rst#Ene.CXMsM)]JR
d,MUFGg.tg@rQrmc6mBp0@+Ea/e:H7()4[F=<Q8/8bPjK&Lrd&aI:2X3d=C#o=uOU@mH-Tu&0_%i8(;U'FDk4.r.-%kU?."d#Pu]M<=K/>>BlG[-:Dp,
-%n?-O$)^gIes2k^@e@jd4S#8ZLZB:EV9q]<Wr28j7.LdF$M9nYAI[#^)_/3qss5tc=&RF.iC+Z>+94L'CN>l_PbF]WlQ-18&OeU6$+r.D[/-dddJ)e8
EK"L5$pcP'Hrf\6GPECZtcC!ZQ?=<`k9I"h0.d@-._8H+r@#-A)7(JXGHI$e3S%VZO+j:F@gE,1:g@u`2`J&b3Cu(^XE2'*b9,0OFaDa4Q%X72HuP*D)
[3(JT-J;X"uWYU:b:A"%F1cXcTQd`,"Ar-2DRHn`?YPc4G22n*NRVKl'8-3gRQcn_g#uWmu-&&S/L_dG`BY!pi`E?7@57?K8q8-D@1Irkk]#QTOIbmV=
`R=r]EAY:E-MV0GiU3cXfQX<pn*/]X@XC#RA<V;(KYBVXdpGj*\;J1Yc@+^:H.%>.6sDEPd"F+hghqcEFpfX]#GFUh=%*idp'<#W8J.eM7+\O]&cU'a7
1aR^M*CIXAd=t?E+#`_=V"YOmJNkjU!S(9nDdXd6Y-0NE8l>/Yo\EuJq&&N`"Xfm0HafQHer#b(^U8#bkf;%s"c7"Jh1fpB].hju%m)pQs+."YYMu6OA
C;Tb,O8[%RO?]ITN%5Ec>I<)k?C;5';hRS1p4i1C@;A7uDrp5Mi%<RO/F&Mo$VgZR/9Kf?5oRR&\T0hDCM:]XRt!K-`uO_^S,QZ4ZZ5umA'k5j@GD,&(
]]BN:2::o"&r9q[>)MXH_-i(jDGD(LU%!k)3(aXIY?c]il;/TUj#s)g\/[0aX=(_gI>gKOm'&@CUV8^Dem@C58$W!mD2POFeOO[WdFohlR>e2^C'',[G
NC&iT2mlqn_GNOWB^"g3M0kW<GA;Y$'"[.5'6F@D([EJ"4K*@(_%pa(nfl1^*Vc\g:`C&:gkoTg6K).>46AjmLDkJ/k;E6W\f@l,gK=La&I`OUr23gMa
e,m"D;:ah'0jD,$m)r,rdn0^a/P8r.bHh929l`j>iT>G:J.$r13K@JBi9Dg#&JQ`<92it-Ql0M<-"W9jjepRI@pUPKpN'M]IDh7,Q.`Qi,<i@\6"&#d]
"Y-ZjrH4*g-c8[Mf;f#uUa(_JTWCs1B'U%5jbd20LGV<_Q[NFn%g7i=-4mB$Ip6<+?j$JXDrN-b!i0F=_%@r-+1SeKb,c*+`%BeY)m`QGC$B-q75gdg<
G8E?uXS=+W,:Oj$$46co$WW5m7MeKMVmRn<8';81eOJ:/QAD'92j;M#*U'G;mN>kTQK/!:!]CiA9^Nj4^ujr>W6,o$cl-p:JYRB$qT>DN6U"$DB[cl6*
)^&;rj<n7[\f"+2p>^Ag-+B+c(8O5i1p]e"2CsX\(`;0&4trt8[7?m9I.&/\R*gj*j])oK8@0U8JFXmP%$WHfI/CN8-#&)/[>NdLN41M-U?&P$PD^Zj'
(,?\>e#>k.+;G.##kF4a"4],#o%S2%7=[4.o^Mf>X_iX'%"6bbmH*JDI[ZpU9soFeF5Co1,(::d*u"3:9%fC<lm9@;smk^H)eIk#9W!a]g]Sf:@7"\(]
K<4g])pe3&B)@Dm@?>o)flK&!4('TJZA^"$4,69a_f)m1a5<MJh?_M1mW1L3d"nU)T/T/_V\C$j4kh9sSpJ)('ldi"@pjM(/V998!2i2P4*,.h)cTT[<
>$R`#5CtE=HE)ZI.@]2C6,-[FD)+`KoF?F^<V#kBhNeH'Us(l:8m3W>>gdBMqdnH\,]TrP_Hdq[g6-t<4%\>Nd@eDgSR8K.M6-@EF'<b?<dcHTE<mD#q
qGaJc1'1"O@%k;fi$LUA^"C1aDgR$Qg@AZob>tYF_stYM:o\<aBMPBG3&TXQO;"80>qTrcJVCu'CAR&43X*,W#P>enXZIm9=B=k:5l/jO*O:ZWQo(64[
G%-=/1:@M9^XteRlcuZe<\)F/OOG.?BnT*)HV6b[&@8%BTnjlcT2/@i]X$]EiY2$0e)cqMLf[b25o\>,;"jQ&*B\-"H+M\/a/c.joIj^T,ULHaT*ug*&
t3]^iBS*AYpI2CA0$`GI[qPG@+d-^8B]@]8J<QQb<@P.r)c74>cTA*)t[o+52qhcf\Y%QJ"%U:d(F5o)WO4mXqP*pc;0\hotpo^jL%erV=M'Ufnth3q>
@2?Hr[_NZ1J(YGK9D8.pBppF_$MPSkq#BK[;fpOW2Y`HoD.!;I^k(0?qt5qs7U(!MOuUR+_<ocho>=XonY:Q^`+oAeDGToH?(X"k1a$g%[XT0O[(c!>5
U%5TZ(,H.Kq]dLVWN$o$FdQ6H%7G@[b&&8*YNt4PVeoGCYJgkdQ;kk?#<3GLk<Zg]XlHF.Q/gj)Mc]d6ENUOu85oE4H=TQP3459%InAQN">])R.fK1[p
)eJ3/=rtaiA#OEM=f0del\jT4E@.glC^;8_;XfI$AC/TB.M`r)+4C#CBD?sTeZYn)Yp]*>08]a$V@c\60I8qoR-KnES,i?n$">?\';2@<.ES!j8):3i(
Z,;(pU`0`3Q3LWlSR)V28,%?[!_;p%<U.a1$_a>"uj43[0,!rMA%.+R"?0M</17?+/'<d7K[%4;/)GLZBC9bRdlr-@U)If/?UFcklK:1fZaBFB]27M)!
eu&Rr7?'/W*ftp,[Wma'Ig:S`4+L[DHVW'serhmedBf$I;,D"@)3-n3e#NRN;nn:=634#([me:204W9Pd\5%T^*dk,E(tX<Rp^8fo;+F4.1\pdMl8mZf
"u;]m#]EL->5?2@SrX]L2gfgu`c?plXA_:Rp:mA33r-S^&nR:3?f^R3KrK*!u#LWqqg'Cu$,UJWrc=ZS2>Dr)9k),3$eM25iF*U.=#6d"'Dm5os99##'
7hCS#V5UUB',G?amWC>>9<M)kG9B%tM8*A(a%;&1+*1=[#IbubA:0GcHLQ#+uB`knSHA/WJ#NY+-<%7`un7LN8rW([EcH1pSb0geg-fmsNP-JbV3De3R
RIjDXB@9@U\R*AXf#;ga,O+&OmUOtr4S)'83T[s9B0$mT/NIGmgb=2Bp&lO,d*2YaFUmGFea(;5L&Qe$JrMDTosfaD!GNN,T.J6o,/,uE"1-hT@u#Yce
eZQ/06h"km,h5DmV\D#*lpf\>UM1e>[B=7k!Dl4q!>%9:kQ>=7]p_pflrF78^,T'+F8*[C7-sdOV,-hpc8,m=jIWkLtIiG$TeB?aaC5V.d>cEh"+%G8f
H`-XF!nfc10A"#B+Y/jWPsl@6R58>dr>@_nLJ[@+e&:daS[;;-V:?2=^!'YC:KpkW;lUF&5.l^UT0hV$[6AHhOdI`anm\aQ9n2(D.n"+7'\-Ne3)?U.j
0\/bRQ:>)mA4.pK]0ZXV,R&TR[l!X&2Ia?ghO%>YmG5j:W0B=<`,jFXb&,-D\'_7<1A^X`GQ1.G6uo'EBnf&V/2&kX:tYNdeLjN62I!IIgC27@ZH-pc,
C6AL?7/DM0Gc<&c\`%KN7l%VO\1pBiF\?HRN8/\471l=lu0Z)(k#mofP:=THAK%&0pGfJKK4Khpi#Cq\WED-0tF5YDCX1`rXb>C;r(=\\io@[V;9JWgV
lOZ*d6?/*jj3"Bb*MT<bT#D>:&'@k8/Ai*#5\+*AiJjK,ljb&sGfs0_dqb8V,mam?+G&Nh/\<p5?#4KIM2)et@U26_@Mt]3#S'"9Jt^#L_#/)S)EmbMJ
)R@L.See[0P+a>^(YTHrl.g/.`4BC=/l<Fo8Qcpe`kqdb0su/Qa,YTVkR0FE?>kXdr#.O/`A'c6cs)bla-;`grY^r<h>Us(:2PTOf<L^/a9[0rCuc1,,
(t=%eh;,BKL&H>o9?hfs1Pji23KcH!CtlQe]u&&-r1_.RKaNWoe<<Ba#3Ia3BmVPjn955.Jj3'(]5GNWR_'r#]<m,Y'onH8]&[7Q(r$aH(H\$4Ve4d0b
]gU%=e:,<%oC'd-)p\pn>q8,U"hb$];T/p:g<)0;rKMk.b#."\XY*[TUL@([b3d47Y=_D;RpdS?/IHVm%-/c70s`WtMd(6Q&>+c)7mC(sA"^RL]<%rfV
9c&2D0@>5a\)PjH$kIpliAK`K5Sk8p]l2tpOH&jGs#_h7tBnVk62qRInC*;6#)^eae/Q%,<*S+FIh=5-.ICQNcK->(Y_cXYakuP,XA1R6>`YA3KT.(%&
L*N80)fbH_.oj@pjFVIC5+6CWNEiVN.^NCaM&!M.S9$n87ubjL4eif>J7337k5QMt4HRt;g3LO98Md/BqAogM$!$d%6F1KlKOai$n+)o=AbL^VYd?7+W
MWY=-I^'cerW$<"^COeUErO-*9pVCGY(lUrR&#F=](nH<#`M%nbnioe6q>D\-UZ,L)C[K:1=C6;*GFThA^f`8lZXj:HEV7_DqFtdVsPQc,4Y.f5]1h?U
AIHVoUK9-B3gEV/%&:@/W6rIes%X,<eG&B0p@[LaM3a@g$q0HcTne?hO>(aVhnZiE4\be@-Q+$Zg"Zi%':!"A=Q.ZbP58-\DnWmT[@X1Vtd[&P4TAlic
g@VtU(4igMKr5^9pF7KUiM'm^k-)`KU7Z&7<!ZdW-KpJol=^_T[`.C]Lh<]Q3%$eOW^CQu'A1YUQ$L>TLcS<jf4d$#,9otH-DWeS?VXQh<O7N<U^,\Bi
mU1p/Xm:K,A4l\RA%fIF2YF7_d]ZIi&XBR,:`%4Wr(YpMe9=nFSi\3kP+XXfZfk9+Rl42cX2*DSVI*/g1l2[Lu<_s^7+c])/92UdB=T6ioTndX]*JgsT
'Oi?5L$>r6&2le32Vp85"%#H=1oU^JDXKgr[.FNl\O[Sj30B'lBGBA$$"p-(n!8Dn#Da3r>l_'e*_'oNa,3=@."HVQ3m]R`::CZAKcj9B`R,+QL`WCq`
FP8ZUYf"X9.8Jh>'ENB$gD2"OoSN(28'uE<LJuc9s8k)01#1kIU'%f#T`Jlkh4%'G<F`2`J$;:og<a<`7/N$&79uA.gf+"i"M"_dYir"'\gfb1%MSKg9
/]GF^r_u&0,X.4C>`([u=qaKPI>a]Tt%pg&be)CfuHZi:g1_._bBm-\%jE:<e87mjSYr):P:1.0jW0WI[``8at3/$*L>2b_!lG]4A:'1DX>"Mb6(nb(4
I?O;]hhXJR+p_c>+)$(D/0Lh*Ke/HK%0Fe02V]H0!V&:QYH#Behn&kY;kKHMa@'Tc7/&d#ZWM2BYr4S?bb4G9'G*V134Hu1UT4Q,aqU26Xb$/N9IQar5
6Xa,_:HR[<frGuTIcq&/!Tn(M6i$JdAQoSJ8,HVN/@aaY6r-+mA:#5of/gkR0om*SlNM7cF!aq\)Rgu^@9)JbiXI#adA?gofE>\d=db0E((u@SW_,k"@
+0`cg14eV![4$TGs#qXDHE"_4kjM)JHh]*^1!=:]5:*88LKiWl*sp]8"!K!U@iT)]AHchBZQ2r]5qt%9MJSU&_s,(sSLS6E7j8cY-L?<P8M*!2cbk/W(
?a_ND!3A$Kt&fTa5U[9)?/<t^A4;3`jT>,KWOGY?JrcMHJP7l]c&;OUJsm^@s-!?kEOli0M-QWT6jgsUg3n9f]KO(V3M3M'+8!]?A=s^=oV=BmEVVq<"
+bT-%>l!F5>G'fn<6V\f;<KQ[RVk/X&=9)3ZDm28I0A'STdpFk5"=<>$C-:m?Jo(2KDHBfe;MV(PaO:"-Oi+,[K/Lus\0;$n0$LkAWBa*c//FlITn('/
"XOU_B_*S.ql8c$]8*1%DXKf'OG#<UqjL=sKtU[9^D!8\;?"HL^66Eap!j8Kf\m0rH3":bh/rH<T("ZI,=?(h,e$E>o&Be08>0,kVg9Ua<W0EW'%b.in
/#ku(;AnQ%sLb%5TrL&C8IZLOmNhdG!!$'%-pcV!RAGA3F]?FTh2C$)[)8=AJ["-XT.JG3IE7+FPV5RJUC/&J9iEWshaOKeU/@;eTYZ!7Vc2+bWK[hXg
G9'ZuL?3R)+(RfC(6Y6CBR'@YC'k-'>q.sF2`M5)o,=ikU.T8LZD^[g'@tU7Qd_:eVhK2Eq&80.d&r]M0-e[1j-MATH+pM@GggK;lc-)j2e3MLQ6E8:L
ZgJoJXo;_a]lbH7U]:SH2OLj/i1=;/3:oo_gpUuqT,>KT8SDpPalEa3G*hA>XS3YBrNG&9:r;Z'"YocCi032JI3Q/HPsrIJ9g9`_!DJ8Qg$^%6dDVJ4B
GYTb$6@Y'0oGF3Y=(@icGEBi*_M22HYuNPN`"flgWh^UbYQF:jV2bq$Fi5=kkhH<;@NU4/+pfSo\&%&"OoIjIJHOKHRVjaHn53$p3INYQLlF<e\E4Dgd
2?@m6NLosm2_"5/[s5"VX)$$>-oUcr-\+``$'g]F<c+Lrb\4-(Z79ZA4+68/fF%][:`DVET.EMKqLc)).?K8FXV,Dpi[99q=N>:"f2UWYI:p%CiC94%6
(A;/+Eb5d?Y&#!G;;0",5Ih)DfSfoQYo_C5M2DH6&D9#rAS=nEKM3c)e%Pg&Yc8:7PRYNh548k_q96W[So?d"&XiEUK2G*1,V$l<W`_X\VniIC$FR.>%
kW&pQX"C+r_8tHj>s3>4ID;u2>us8&%e$ek3eEP,Fr5ffNqo3_n-`A@G"r`kYq1c/LBZKaMIQ$%'O`)=;d%km92pEg>"IWDM.`7Lg2CZTEK\PF&XD/dR
,7*`"5VL+)B^lprr">UiD'O'"Xk6dN*RW`&dds!2NeFh6:mDQi27*B*1h=f[=(\N*mVK;K#s?<:8OuWs6f+OLjg`f?d'C@h0V*0#+TWK;S@5XdVhg%OJ
6*%%/EtrRH9:b`bBl?Kh0/Lbe17/0(G5&)C%?4Vf$Qe+6!HMEO<IF#!)a]jGRTMOPC.q+FO&g7[=OH#fqcT[NnpIXSi/!9?&,KQEDZOi/9-*a*:cOW1N
Fm["X]k:)3s65D#3q(N`DTeV_(.8Ko1RIRKI"lX?EIeZYVjV.$ds-mI5,p0UZ7C-c:e5"e^W:!F:hl%BDHI6j=nm0F4?l)!m4^VdnVp0lt3F=P5hM*[0
P967<.P+NphQQt)r'T+>!j*Ai5'/FB(V[MX8M(8?c6.)CIki&GM#LsijQYl4>p+MnVPf>YNPBN,pJ*W=.\\i=)HM_`nk&lbfg=o[NFD,re;coH$Mu\n?
MHdh?3;BnT=Xd3Db/!#<N#b^m67s&%1$(IXS#fW;s&Qd5^"Y@tC&HL.WW5N[(s.E_#d\gSa*.n\W+Qoa+sE2Y?Yj%nL@KF:\5F*c-XC6#j:Ii"P^+ChV
Kr/i!V-29S+/K=RgE;"*&8r:/ZW<FI2<Tjq<gQc1*`9AH)R]$JC$Rdir;ZV[WMrgBS@^1]KdD6,[PQVT&MtOF6J:keAM"+MppWj&Wmc9J"<.>jMPK5Yb
Juk/,-`s4hS6Y#tEj?%6P"s$d2`qj;.K:o"hOY..&+$0,5oMoUU@/5QAQ!"N&u@E>+V!1AaZW+XVj"*Y"MnfSW%!CC8@Ul\1VT_:C1D[LXi(?WL2EIXQ
aU1]rU7@1ZCdfT`.q.`oWNEmRMe`VPN4JaOSUn+)]raSO^T?!DuubWS,fKHh1M)ug3aWZ>\_LO(M)g)Aq$l6F_2$S&%c10<,\'K;]%kD*1sT/*WrB/At
WA)3F6)SAH\;aq10W-#mc>[-A*>?ARP\V$L%J6NCs0Cf'of$>fj&_`E34+B7351Y?g>m\L1Hu7scHOUmIk0nIA(db0j'u1*&=;Hc]BfPOkY(f-d$)&Zq
SL7E5+\1V*pi[_br\guCD#t'm'8GpT!2S"dmU,U%$"37ghd"GifJ'VW,2Vc%ni6]73.;L*O[E634`6LjO>&$3GrQ>1"#NRS8^QaT*e6-ODK;3bX]J\C`
8PPAOJ,'pe]GB%&dc;nR_Y*lA7[X[0Fh8-$,m$(Hr4b@Ib3W%Y""T^8DRMB+WtQ@#/CpAj[qV55JLbES*3Bi__<,2;:1+!Qoc`iF7dAr]&2<g7[Uso&d
\u;mgD4YRt.qcT^Sc48tmJF@XBE26CB?I,^WO[i4FU*NOl)>7^$V%$Eg\GCCF8_!;;US%#%#:e].,d#I9?lq1DEI!<5Z8K<1k(Z.*!G?T?boq`FBT/79
6^A)6dN!4Upf0Pd94!aPuanb0N^ojMstSM[`MBQCh)`JTR!+-Bt"KrA,iNs/lh.t*@e!$KB(1s0r-a<7fpqj>bVj30HjQZU,MVEY!H,b1OZm4cge2cc9
O^dRKi#s\!&IlZ+(m/_(;,,@!Y^Rt[/_Ck;n/]S*sT\dO59"0G8E5VWb>B9t'b2t9%eDIQ?52Qi`D,H$cGJuNK%c`a5hEHS'0LDg3J@:9]l@n]NJd3^p
?A1asN<BO4alTki%P9aH8Yn?)`:YoFVY>"Sq`Gf!i=bp2NE/1R7]]!TQn]$V2bt[JFn3'a_\lEpHq./Ja@"^L,HTD^0(l7F.2,ca$0h+pT;8Ka^OI(A\
h%8!KghZVp;<eU'je@40bn;BJREJW)*sYZSs/#A7UII,`\jdh>l"7.[NnT#-.1pg[Yq$G<tL#\WMf@[%K_hM^]k<7696!e/k2ITkU^9;)gi`jiWSYHNm
E8,%gKRJdOJGLm5sd',*S$^19,_iA<TJ<T_[Pt.5Ms]"9=si3**ZnI=&;/]9XTFAOgL`#[=V+B(tLt7*F/DZf<e7,A:)MqCOsTE.T3=BHNfA(\hVs(9$
,aO4LI>IU400ZA-:JrXQ;Ee112[ghT>qTFMV6oWgAr.i0;r3EUlI3Cu4i]nY_V?f/pa"p4/DQ#*^Y,.knf15Go(jub?"KrX0^%s*qcOT?Bg0(^3@k4)Y
K?:"Vr%FBM*GYTOlC)t9X&TE:*iHS=@s5,>A/Th8pM:lfrd8bar<6$gt2!or6ArZi_d`*NhF5EO,Klt[9.bJKQP3mP>1U`ou$q,J@Xd9^8#F\rZGVhuF
4*pb,]+#]^qR]mUI9Rc.i5JN[eLI`8mW>mL2C7hik1`/B/KNtNRr4dTX.uq-5+3Q1bo?Y'iFB5,h.oKs?@s--:H79:NqOmMJEk:VGNr#:-u,K+/W0]'0
Y=aiT$X0ih9si0Jp?,LrJfj9$+/#bnc/e-PnYX;g8b_K+Vk?2P_6bi&YMA>X?_T;r?g+)\WQ$7qS(63Ht;sViSg!7RY:/o"ia)4a[6+uU3.bBeE8*BC\
M5k18K:l76@'H1i7q&gu,!:7E\5e:&n<2j>E$p(-Qm\@(PK]1Pc_!8;5<p>7UT?e+alcmV$$UW>:gBUl*6',dN/uNTmm5.i\L=&rU%-=4`nDF3!.^2*g
?X:Tq<?ce_LGqfM<J(Gmk80bf36T_XO!SZ4KB/7l']Gc&_4[su6qYTte''"d.Q=_Ps!>Pg6?muUsW>A6I0]$PN?]rfXgMX%erSC-SPk[e9:Mo0Au)LM-
b:8t@C"O]kR%C%H7DcCX?!@3/o$)*I-cD+9`7_!p`j9LnaG%_9(cZ<)LLs18E+,lct!)a&k-1TGC<lVguA9>.Dp83\H"%LrpHY`G!Xo@_n&i)m$j<.\s
4E4ho**eMdn:<B<UhgHZ*N/\bE,YS;r2@32Y6H^Po<YXHV3sJLr6'0ZQFo`NTc80(^E0X"E;!Xr_g+joLVWs-RtIdY#7rm?m.4GIW57)nnA`_!4O5@DH
T.-Hkm4DJVqGn>"l@]65HIhA<8k,DqK'$;,V==g`B]YG/>KE01MhE%GTHecVhDZY^e'&O?[(eU`8A69s,sSq!?fncQcOLj9*p:f]"'mU*EYra3J,FX_D
`jBg3(Uo:fr)RJ8O"["^>X4:)OR%TQ`^S4,`0.I%h'M2M=mMEYOl,mA\1DRR,Y*&IHobB4h+9.CNeehnA.,ja*t$Dd]I%N.aR;j6esQT*;B(Hg+OC2?*
J]i^QoPS,(Ne-L>3Z7]M4R`V.glOG)3qiOV6mi\07q2k;%B40ra4ICd?.YW2od9@:AT$$>ap.r,DH'"#o+mO5-bIAXH,SD3dGrCt@V048;$r\q&OqLbh
9p<iLJf)*V6Dmn/'[Fbe%8jg7oQm*13N^AhZA4Y<$a-rgolN:XA#r(#cS")JK"t@;.6gl.c:Lu%$,)R\cHHhSl-RG#rZfKIF%#4He#;3OiC+P?rn'R=_
ISojf*hl1gTct1)@[2drni2jsD9#Fm%COKt1\Gsa>_)Yb.Q.d=Of9dZfYK7L*[A(?]`#[SYMp`RnT?PL`aQ/[0G+0lbR>8oe%-uX.>>m+!GLl-WsgWg`
Ht#05>+aY9Bt?^0)m.Rl8OVt.0cCdW@%p8OR2f#.oVB?,TM27N@!nn?%j*N7L',VnttGK@HT`q.4i4teqp]mN3f:.rOAt@^Es-EZ9p^2;G3fK%pf@<`q
:A3P*NlDi=b'0X?WRH$U?jX!%/7s)190UIc;ZM)=`eCSjp/gOE[1L%:LF5nd"Z-0)eeEr,L>B-C=r_bt-A`2)l?0N%V26EWbpl^@EWp@BNZ1&=#aeF.M
oRg&!UBYP-,mC(^qPl%4'R<%d%7m"NM\5)W-sbl@;$*<Z%h&WAI82<KRsd^LeN-=(%"8[LTQ:WJih]Dh_6e<5[m,W%36:)M"dd6WZ[]/FrZ$7C2;B5!(
"&_je$$GQ\f5D0DA.-PsRdtV8T;F9b[\DpCs2N3cX.HqVDmg^gZ)-6D'Wp*YW0^K]`eH3i9fiBI`Yc:0Gl0Te\[/buLLDEW;X!ou!.R`i=kEUs<HDVar
i,B%s+rhbTjO'AsQcQckR5&)h]qEe.dr"T>1^2K._g8d:\q.WR!PqSC>FkR.<^TicIS<ME\D@oV3*M@)N,>:,UtQ1c'p-!8VfTRRD#a(Mq+bIsA_(LfK
KlWFEX2:^%@1IkfL2<D[k&;h]/%4,aWQjEm6f^M3>aGmTdU<UY@ao5V;*7I_<F0!RhO-SWaRZa)jX\`*!W[l!mW2Grah<C=(tBLR"3*uj,Y^B0s$-d5+
LaJj\/lkUIuVb]Gqb.$0)5NEQ0iP!ePa<3qdUPX!_IS!pO/b`7oQ%1NbcFes/qD"]dk^_Q&mu&POJPU7lc@k::=-B<$qt0:`JSTfMt"L`1&($G78Zbs%
8m5(N&H+/HDjq3T'KkE^$&/*Y6(e3YQ&<S'2-\!W7CHDY<#5`/u1Bi.Pjf:Jd8AhWO_>@t*s]Fo5s2n&,<1H(sgW7I'd$p79`89h&lCRf!F'ZJ(=DCGa
%g=,tTR<-,f)\!JH;B+G*L61D&4u$U^^p?eV[8F'<\W?X3#%e3r]6b.r5(XD"g*CiHLdQm>;pHeGiLU2Y_#qWiIQ\g69,Z\1P1&eA,^5#r/eU>+cS]+o
5oVso9q0AUW-OJ]]s$Gfl=Y#iI&`rXC(`>)a8,4mYX2<L9]+=R/_B7kmNos<j.[0Ijl!/ir'G_G4j:FL4^QG"2]t9.TMRY@,][UEH/!_%Y-!pZD\d6k_
"Gos)PCbR#+jT&areYKR]4g8E:PeMrYZ$A#^Hg^l34c>P"V9E/Os':J-0kK,SplB*nZW,Ie,uXd#O(topi+WW`Vua8uom0>B5I;SBIDMdBi:NN(bi#r(
DK%lH,[3BhPN/f7jLK&duH(\jc;I_aG$o8I;t;63%qF'<Ctudl&65U')1+Kr;%820@R$`ZI-^Gdo9!8\W>1.'oi"/T\f0=.*XE`&[clL]Xh$!UQESnY%
9;embaf.Ygt,V10imDjT5bTRtMU`bg,S1'G.7k/2J2YJnuU(s.bJ%=6_>=D/2Gki>ODDd!Vp[X1@i?/oSIYKi>ZI2N,t$7&deD0kD"AhLN#:,BtD*bn@
^AO.QAVk]k3O7Pna:re1PMb9Bg/I=&:)`fH=dC*;7'+G&_kZ-q%B8U,/S:ZXi_&!F8$Bi1Q5:*0idkZ*77mQT>nK5b*gB7L^Xm-c$fteLE#/GusFN%S?
2]a&P;=I+0!4HKld@;lb`+TkH([Md?<YiIQ-k\9>O,\sMSNWc#=Zq(R1f``1VsTQtXGO_p)h(*8o"1u@:Vc7RkQcI^VV>gEj^A7,#S>.FXJJkAAi<Pmc
KD3PLE`qG!LdSQf[T]nKSm?^VQhp`NLbm8D[+*JW?>p9,Ir-S+k6hr&geV,Fn0b`)]Hkk$qkV>@UjMU]#t1\#$s+n8%+^gQ<K[u@Ue9IS`YCci5X2^(C
>i\bU]#HJIdBtec0Xr])!V$8\f>u8HWe0h+DWiaA@rt0hA_?1h2pJ,[j&O02:[EP[Ycg$fk&-au^h`*2R%b6'!rO-Zi@I@<K<sBL'\dnj?sf9)]`^a$"
LZ'4s:=.;LZBTYWhI^3AjIN[9R/kW00)@L?drGSc>c:;!V-A(c%KB*?<+2P(DFCO*s,Dd?f`aXZ1IpF3jcP8bM6-Z!^H,hrG"#R7LMGRR=W7lZNN1*Yj
XZTK)=Doe*2T5ar+KNqE&Z>9fS+X"?s1^lg!6JY0>Ok;qrILq)\>LSdE8+k??lFkclm.55@KX;mQfFn%]&Cu`do9h(]UW)+C/q"_Gotp2iHbb#1_e4c8
i^@+)Xj0--25A'5YNpr/e4=m2X!g!XK;mU'SLe-g&s^+?iV?#fWO#_7-*4[Dg6EifD?_jQO?OO0C.hdf>c?q_19B1dWZe8h-"8Q,i?N"J^'+]^MuOhKG
-e2WTHl\@84ce4g\oCo-+qDa#ID@f!Jn,aSQ.A(L;c\iqJSWl(LJFlW3@P-fq:cl)77_\-8#lpB;0YCor[i6?J41^^gK1/eVt:p2'dg`8C:*pJGIt,cM
^QCUCkchO(f@(N3J:>H!=.TH`f/f?qALP5j7t!"R&5u,<9f6)WqsEI"IK:#2jK:MA#!h@R@_20=(&La(cV*bWK#\-(YB]$'4udOH_G]TOkC%M#jB_G>p
k/rA?39IUL'8HiR538R@cK[iMWV/Xl!:rI9`DaZn@+nOW4FU>"%.CL8UY.1\nXK97*hZ2>J09+kb/`8Aq[CdpN#;N8DbBM)WjI)Oea&<`5q8umn+#pIK
sj)tB,Q_b]D+;No8Yn:8g:hqIYqk=el/`#[c3h"mU76Dd==`En*Sk5njJ\YDP5_.lZiY^S*bei2m]r0J_mJQm&[G?+O5i.!Q103;<P``9`7X>i<\u=4V
rq,ITnQ%f!i_BUp246]SHbMCS"MN!cQ^D,SA$W@9/0XN-(M/L_oq]B;F[F))Y_t>pgF^*3#j%\6cA"kE09#iThXrGbg%"oXpNO%2A`/nb<lC-J?E,(BN
I'lkNX?]!Xk'1):TF7N"8bn0DukjT&SZY:>h05sY[?)4ZGt.W_+*Zpo45Xf%K,M@/@Vg9f%W:8%=O]onGP]k"qb2I<;NB]Alee5s&>ipn[h#Z5d+>]k3
\I`RZUXq94fRk$qr@5+sEFc>'&@)1@L2H)BjlBJ-QGoFn\M&^G]Ou.?M'T"O@&/*<eT7?fSeEXT&'^=7odG1fqc]!!bDT:Iso$@D(<F7Ppd9<auJKZOO
IFlEk1RKX3Xu^1qafh2PbQhJMnT?Mhsn/rmVV]_cX,Rl;q[+mK^5r:7BaHJ>f_+,$4E61L=PT^YBo2/_:$h&\#HQ]_U=0m)\XM&kuI1G],5Mf"V.9Ph+
jC#k30Osn!X!15&ZX(Ye`3Q9&foG7bOKhp=:(^=*f]@`[!=p^pp:*Dt;H5.3%>cnVeK4`j#K(1[N&V%=_epf_.'tV&F-]LQto./m>[_u6DlZM=28G:Gs
C[GoZGj8,G`=Z1o@]fK;N+QreLC`f9b>[;^]Y4&=1k;ZAT"X=DG'h;K["(*O8b`,I:pGahSrM,jP1<8n*^$d.r63sT5BN@YTcX_Zn8;X/o"@.02Vd?DY
UcC-[EL#"Jah/4<i+Fo&!O%kLY!<-asGH=Bt&QTF":3D)YnhfJKqd2=0LY3NE@3a<#=foqbu$#cKg)<@/9%#i_U9R@o##XXLc%6n<GB7_95mT%a#uuCH
^J*?/e"([%hh\/:^n%JDk[eUJU.9!BYd!@T+jL:k*ds4h_Vb8B[N]AG,-sX['YQ/u65O7D"K+!S8?0!Y_CN4?c,eTQVGe+d8iX5e"RX)r[Q%^=\pgDWH
BU*@Q5T*<%-\GY!&Sp)YZgJf]+G#T.^:p\WE0Naikh%g3E^*7IZg8m=D$(u3trm3cm;G5unDVUcMe<>OSl&GFJb3NJ2qbknNkkT&Ro"KXepA!dA?K,k>
(;6*fBb*VEHjhcPCP,XXLDhf%54RK,<^Bq:l,Y^udIl]cIMCZ>FJEb=;JXuel#F]?B%k*#(D()7Y+TL_ekY1]!ZL2oZ!g=;UH9d@l9W2IQ7_U/10o/H$
:ARBi/nK_;WjnlggV&!WIA;Pc&S%7rq%WDaoqS<5P8gi;-aK<Z$]Ws8P3Ii<:0jn9AifbNm&&$;kXLW546-L;5#$m[:1&_MQ3*g!+Yu;X#61GX6I$ip(
kf82bTSO,ga35-U[+7N)f3!sn\&hu\hY,I%$q:#SM=<OWf;/kg'`!k9G97?N"qi?pfD%e7,>AL/%809PU%(9^hSA)7P;F)hHWS+i6DRCBe#"1(d36J2'
p#'_n+(X)`r!7P.'IJ>b@Mj`.E6N`,h>e=:2fR@(J0sO66.bY5PBij09n"XnM-JhlLJpp(2;4mmW)e8Pl^4nEn_qZ=P\GCn9p*o1g.U-0d2e0\6?u[FY
*B!<#$YPRBG,2)*D5%3J?U+[t1C-%_5#^#XM\nJJt`',aUqRn`_-=r(hu.Df_hS,dq*rYkL@Ztj=:YI*\;*j?F;;g4]/)-5Dk;39Sj`a-F)Aq2Q5>>)5
_ppO%p:1I$65t6H3*f$=P!HqtD;fZChaO;UWB/"6YqEs[PGJOmm``M9;N>P>FPJ-"AO2@/k%kU!bc<P+;87(2#rKEkRVnYH>+9])!c*3hjW'WYaQ!7Gb
\*,G-&338.:!sbS0Mrpf"nS)%c[Jd`q#e[N$_p\Z`h18?,TJ)sDfIE'-;Z;LI:^QT!t-Wu>=<OMmUnhQ)OXa;;;f8p^J2R_iS<R3W0+sON_B0=2mj<4?
4HK#SlCH7C_3.'=PFq'rP'Gt]FRn_Z)U^)(AT'#SEbNi<`ju@H#mJ>N[J,YCRX6!b#RX9lX304CB^/[_fM2X[-uQ?/iIZYbnl7Nfunb%3qVUhU*M_#9_
d[:*X.QH-n#Ab4ihl?Y>pI:$_N_nl8$;Ii7.*35Aa'!T/raIC[80g)&I.^GSqUumYX.-D]@BLFk'I\lkC9KCV0uek9:`9gV1tgLG)jSo12-1Wgqg_/^M
%.P`^UPrr%_i'8Y]B#P_9?.dg.EHXbQ8)s22(oK;kh,;IDg"GQ/&nTb240Ob'1.es:<-/VON/DT.u'3>@7R8Caso]kd4LR_k'AEM8:d5t@Pnr]rAl2eU
A29k[Y%X%b*8G23-6fn]%PJfV*gXR/$P5".&Jh]pshciOl.[VR0@t$"u18gT$IPp=U'\&/LA;hKZhLGk^c&LE?fcE(5*+r'_)TfarNr=q;);jTCR3.Nm
!!0HY!NjiR]:N`,Z,C;P!WW3#!!HG.'''
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.60'
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