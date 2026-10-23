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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 55):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE'EA+5s6&_Ti<k`>)dNFULdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%NdN`;%MLm
ps(uYZIsn`!4C?*kQ^3^h.\E/^[&ioqbOq?DSC2&O)s-h&)ENi]k5Lr4ELnQZP_kC_NY>:QGhjri,+g+1S/Ga97(3@b<"kMa4!H]O7Oh8KeM>5l_)d&@
a^qqG`kGo]cW39%^/>nQNImG*2o!'n`?U:Q-DIm$Ogc.6,dWE=&$Im6jWR7Dhjfhi+CIoh>EA`snXP0os*X=b>2*?@Y&FVguS!4>8g'PE/(^%GW:.p^(
^!C,(W9HXV9s2T^13i"Fd0H#V01E>O9=X8$)DaX]Y4N?(#_gs8-lanjOV\HG;/imbJ:-8ouRFu[oIB_"8C6pEkaJfl3rTC#)j@(GA)gJ^k\*TTA]OKU@
mU]MO+`nGGTFl[=bS)qq`oZAbb=e]>#6=/4I&84GXcg)\t1D;)c-UY$J;XN?H6kHPe\M?A-PgTP.i.VCcQo__==-P::UUYmkM9Js?8`\\q;jjC&:*P_E
R&_l.0(@2ZOGJ#NTHLP`ql`I]'([3kjP:C"@8YWm3aA=um-eIn'^u=TfL"(Lh65#^>))5Th;*<XZXN%XL3tG!cYm&F;=57\pM+3Z<7JZZ=97d^oQ1l.7
0$.eoSt#]&<d?0N:pY:_;Ol'nWji+4H/)H;mMu;n03hMWPZZq([CpPl"+B^jmpc4KN=0`@a9YanYGetJY4#AQ`[@BC9p,'^QPM$S>Zlhrd8RsS*L\i!q
TK?%P%Xf/0Q9C1&p/cB]LfU6*9#a"\B"Ni2ae6_E5qS<[.(kLVAL^MLEIjj(";<N3-DJ>ZK-dLl/H@e&;u_.&Xi<H'jI[r>>8WJM4:>Xe[]B!m'M1V+<
F#*bio)_6a?c_S#`u\>'a/Mi8kP"fA9q<u?om%<hq%\e9_+,qhpQR2[J0XV8hPoOC/MOZ61NoYsP3I;$/4mr\fp\2%8Jm+12d5J(unLE:SX,L@m\g$/`
=%dg^@FctF:"_BuD"XYeC3Q?0p[^m.;H:Pt"%LJAN4pDAu01*(h#8;]$TC]D=WQ!%f6a]U-+&257FF!rM,jNp[aW3V2cE%=?#NU>IRJ5[ZDr3^3Naj(_
$&oSg5O0^u1)fnm(#$DoR?DqC(DrLSkep>bC.\+DZm@Br0jF1S,XNIF5pN0@Y"p7?O$R[O7F/ANB?Tba:k$*SRmO`%D&7%MUK]rA0'VDD3?r'g$,.emm
6Ce5h=`n/3)HWods*mIeM*(%Eu0htVCMO$=!$E7Pnkt;;P"bIK15PE.A@^5"_l.=I*8o";mi9Z,KYdfi-21E</)nh+!Z&>dsZ@s^:i91Sb6tY;/p'0C^
/P)BP"0D,t?ttWC%De3cshFW_t;bV07O[.jK10B'd:hPl9qf^e,kGq:$!WH,g'WSFBpV0jZ*BSJDE43.m_<n)KkS_=_ac)c:;.M;*Tu.Mc2^/Va@_j>"
="X;]cbo3+YD3s11:V3.3n`g*.FWdHDIOjf8ZF795GqDTV0c%G<H+HLr7(1l6hGpPh//<'dbOj%cW=npeH3OK//;;71(pa'E7k+pJ%m&]6KigQGl=6BR
aaHH56LhcOP)Mt?I"A#F20-6+O5Y"rh>>51#(HeBN+QN`kkqcS>?=CPZ+bQfJ/eks_q?4X+OBU1SN7&PpR.I(1O:=K_&8#3J09'O^"`F<=]/$8>;Oj<5
QCiLcH\%.J4^A@3n[mACIuA.@D^3m!b4^*lhkAL=h2^fh[C>Mh^FHD$J\sjnETZ*qIpbQ1+&UI.F5mZ?mD!ae31!%<1_jXkE%t#_L$$GqG]CODSVTe94
\0F$Zn9g6.Xj%Bc,9B:Ys/E-;1Cn=YdXSbKE#6i,BLX.FF>;^MKSVS00du`Qie#/l6m:^-Lc.O]0Yoo'p,(im8m6T*qlc7'VZ0+G)u<BctTUa>`Q9TT\
!+/&R_F&BZ=b!W750>q--VUA<4e@\B;T.fJDE]Q&]rUTCaCPHY0'<;VNP.;:mGq0O@V<gmO4CM6.5Zn\VJY.6K<CKBR^5.OMpPZX>U:p93#krSi$<pV(
XHf!!`JB$E*R/o;.HBq6H5`OpJLH9nCQc(i5njklkPYWk,46h!#3Ro'2-"<PCG5V'm#*b!]NNoP6lj2<ib?t$`@F;RMP`p&:LePmk@TT)NkilM5F.9('
?]C2bmh(irh:VQ-J5"VaVh&#5tM+5rF\Y97Gdcn:2"b8KPe6G&r[=S(siikMA,NB63]O#Z=<o<#UmEfTt#dX)U3d=:$XMklp"f"W;i'A"b;F;P!g8Ua?
S&;@\l`0?hU&)]^!4&i>BdI"/o>e)M>L_q@Z:0\@PBTe1ma`tV.t7W9$QiUn9#Z[l'I0#sLt]D.C.p:p'd^<5Sj:X19U6o*UAG`$.l=g'V?_-"$\i\)`
Bfp\b-=XBi_5Pro83-ZL@iM)*(NuG+_a=A9o-[t!n])de@Y1:D?Fc6&H4e2@f3a5#9[q$U->TCM6YbApsI]4Xi&*A=5ZO_'<rgq9(JtdO8--?/9Q^o0u
m1#0.JCM/pbmY-Q%Ai6F[n'"@hYq<b.C9s#'\W!9$CilXoXRfaG%Zk</GR8s*.m)L-5R$=M83q*.G'fK3lsl'[Tp`[(R[!4as;*L?GE!$4#R?q4F-nhq
aLY1ad:JsTCCMb)f\Pif\SD\H,&HhJA/].d*H8i;jd&l[90-8T+]lY`UXd0qu;g?VSm%gd+7$S>,<NPR.NkNi.&!L5oBfj=^@J(6ZL*2aru+M15,lWC@
P]4EHgcmWk#Vcu.nEcb.bnr)E/1hK,@Pn1UL-1joR3#.i;rZ;eW:*9c$WH(Cm-q(-dQUc`eoh+nI;Yai8L/JXpL'A-'lL[AOSfW:m]?fSR;:pm)*o#h;
<+UXe$h.@&k<mn>E:A->CDD/f!;R6XOa_b:k1%Pi]ppLb7o!dUeKk3Wg1YVt`'K@XHrWa>;=Ru4%bM6s]!($;")cH*1FWM*K96!#LT4,dI]18i&dY<17
7Oh=9'Xduik">2S%X!K]hYSln84?d`]72;A[(23\j#I]m=hG&<1L&5:fWZfC#fE(ddT"X_rf>2,\]Qd-tWJ_&h8FcJBCO(VpM^),")*NSPrQB_/bSC$c
1ZelpRCN>@W\J?4MQr.&@HD>WI-mmHM8k&M]'dmpGYIqi00(PI5l?5idUm%[3-WIN97h^,WQUHW6[4=[f,s@fsAEL)j%c4Wk6=f2C!5%*YEY4CX%sF;=
Q0B25EFJ*(5rjW)r"9ZKjI)%,*X.2>/hZ!$Ti2r9:W4^`"dTmd^3:e",ar-SQ+D,.")K5I"BlnUM27TsIDB41RZ5UkI]/4f&X1c]a^CPe];jq#^ih`Z^
K9'RYj_C&k)322)0<Z)0fH!G=`#WjSf*qq0QX4Hu>U[hgYa"_J!;E-9kXR$0g$M+^):AqR`baFYa*2bD>Fa]!ZIC.U4%"*Q`5]uoNnZL3[R5k0(<-Ie^
^J&;#RjsHY6*d=GegN/pXkemA^UP8Gp=_d]/69)8et\X%7%n2^i/)f\HU`2YO.W)>4krFlBt1g-:f$A)/])sfH\6fU=@`?0#1;n%!?jr__$pIm3Vd6b_
A.Q:mc%91e;(<PGgUh.%6speWnsuVOUcof$pmtgIAIO(cG&cF15S>^MGaS(-QnbC@S"/1;`n.Zl'$AA#(tHn<Skm`&=qj+F+[$3XLs_sO4^8R)=m+6fm
4el'P=0?a6NSMm?-'Xd!l=hKc#AV"YEG.Eok?.3`(gS.Pot1g>"aWOsZ'c9U0Jm-PrY<>RZ*q;^nq:dPIgL\ktP9iik:2Y-a!iJ!kgK4&.`fYb7>T;P8
Afa7b(,<H^;+@o7;)!4c'!ahLnPh!fqC^(R"<KA%;^F-FQLVQdm^23q'ik,#IL2V5&U$(oq_alKThKt[<Q2AXf2d8d7L<PC'2;TLOIOprg6#41hZn'IU
pN13]npr.eT$uUf:XZ'L`LB%]LdJ^suk]?Co\'*tXG8&7a$/"sFGMXVIX$m`*njmZ/JBhI6*4@%B6gDM`D>j;u,>9X(*9uA)o@gtXNojC+KWmk')I/I-
KI<1L`tZKK4M,ke8Pd_KUpCK9je-lM1rVFu3q.,@=MYkDVrKp%#EiSs\)1=B;c7(_"qjpq&ReN9X`3%h#o%k]P*F:_)J%;+&8%br(i,J2](1l<hq(d2;
V`M>nf&b(4HX<1?"k.jiNd^ab*L6YpdWS$Ep&5+l+L(-+n/-^9d.[cIjb(%\pME(4\u)p/3bPm;K(o_qF.7sFs@):b3h#g8Y^bqoP249E'2?DH@OK(d<
h\=e'?`)jA[5H8tgBCr[LSm1DLUenL`1N';07#0=@]@$l[>>[VDsXN,"]_LA$Ds;4'Q*=J"dRbRZgM6S_nK?4R8-Sdt"D%R&5EI*TY^Ic)@hBY./@ip/
<`f\ArN?pPAHk'o?L_&o(c\0n:ZE48Gm@Ho<V3C'7PV`*jU/\N%uTTmQaU^%3C$uMo-Ls;tWO?htQ9OHPl4)t1AXM5u;C-n"S&I<9E7__ZR6G].2[@HW
K,ZP'i2/jl7J^k3TKsV?Y%tAjs]i[%jmqT..*0q$sk6I=?LhKcIk<D<:aIm(jEa2)IP$V]<dF6a*(Bf9Y:6/-+rnSAI%;oj=P^aDI:o?NuNng0j5:!6p
oJdlrB;-*Kc8nDS%K+SoBq/Zec(k\gc!^/Z3_U8m[kO1m3pj^clCA1H07d9PXVma>86aq55rOS@C7"'-e0k("E+1$q8oOp%B7g\M?!Z-9V(7kZMQ(QIo
6i[>plqP+^mIQk4"TW3eaW<r@&UKum-_(+liL:q\tVe^<$^%gcj^p?!AT#[UaH.BM_WH\nd#4@c\A`8dokK:8sW<*o8?%eJ7K?\#HIKi"LeDVML:YPN>
qq*5&\eY+Zrc.GLH`!Go<1KT9DCWhtk.r1g`7cq(0O`1niV6[5u]Oaud_Dq)&gCRd-GGBOj7miF+3sPksMM\?SYF;jF-B3S,M2Y$*]*QO6F,8.oK0oX%
A55FtM!)ma%;2.d<Y'q?/W7.:+)1FjljTBCWW\</4mQhD2m>Q!g@G(Al3AA;H+c&"%-%nqe.!6.Ad31ebIR,.$A9u3[jB@t=7J:W/gn4DgN#p3Gp]=U.
43.,s1-n;W`',*N`;g:.-7I"m?]Q>1ch?\8j-E*B'(<8M'O)0#qMeroF@Q&QMYVUFG]j.e)&Togt<>o[NU`Y*4GXj]n(P5D^8Ebe!R&!\:mPAN1eVBZm
L@L?;B/8qRnD61d?tr?-n,UKB;Kr%'J&.5JfTO?t&LojG09$uP4j+Se]Z-'T'[m?B1b+`"U?r18`K$OOWWH6F\(h80VY>*RbnMk\c2*N45bm/M'CL"SJ
nKVfdokg%Hh)lm72)72jo5;:$KVmO]>#V_:et4DjiTW!A^s[2)e"L3d"INc"S)f[Qgsj6VZgLU:?r.3rdHZ0-aq=n_nr3eWNc,CXi!NHUAD88jCgD55Q
G\]=?PXJPq7usSQWdZqNSp<$ZGA4L'i=CiTUR/?ZI9f.jL0[W0R5@M>UNY(GH.2+81aQ(GtaJs0'\AcVrq<%e7gO$-M4FAY'3R&[l<7i:/s=&WRgDI)=
t?'G%Rsj@JFHH^Li';_P>1QN/%s8Q#Jn06D7.JdW>,,854JRAp8/SeR'h\^D$ac&p^N9M_XkZU1L9Ls![U+3heBn5eHR,r`kr+[s0Q?!p\d@2.E+AH\P
V@@MHQh"q6?Z,'b"ib4aKgI6r4:pk8[bC5o^?<OHdD*M5OEdZ/NICk4t*DAKD/X`I/+q;8O+\RjZlZtKjZAI$<i6sp?UBC,q"%KKPW&.rkA#JX`^&:l5
hstkhqQ;,foV)e]Hh?DJ-PQCbK\p@\LJ5l,ZlB0AT;cqT,;\/b!\iql&gmc2q=08V6SGd%`dHD40*il&FWKP1j([:#UCE_V`pJ?!pE;oa#Fa]o$3P\L^
L*-';&6N')qe^^&YMhD?3u08-K0CVZVhUXV[hQC[+tXHe]#lOYa-#a%@[k:6V;2$.iU0fl+4X,i[I=]Ga@;[iB@rA()1:0'/A4cH)!Hnh.&<$Im>)_%^
JT/DX$ck%"O!s_'Jp_W\b`sE2:e-h&t&6MqO%;$@L^%jac5?gg2Ej16_jl.5XtJGcjq`arcDGDW;Fk4sf;l(Kk8`WI/LIU&>4N0XN[*J#R1T:F*g9]&9
Ap&3\[7LGk8;?(ja$"dmUFGoFrj?e(>4dS+=4o\klr-cRh-Z<?27X`7YMO!a::0?JK*RI4tcp*BA7\VB>Gpk59E2t17l.^XXaCb^+W+K:%/$O(O3pnS_
A_,aH?7Zo$J7TG(*E+'`*!#ILIbdjM?U..Pr18[krT3[OF/idG+RKcadYQM#_iWX@<d(?5RI0>A[kLn7O4,@+gNL"bu/IWun6lKEOAU;I8Ms$k\\;-=Q
#tbO@eiV[52#Hs:H:_S3EK_cC.Ji?1OtWue,oHCl:M]0)?2G'["EWc)7:Ga+-(3"sTqM>GTLL3pM!R7mjFakhP"h[4i4ZCn=s9D(]J)2`WCKu`Q\+7Or
kX2lnVYVB)$:U3E&^E1p:E\LZZT]3pZ./dF=nJ@@(XZT8K`!u3a\Rc46jKf4(msJ?I4%'@>kbSk9;=UEFle6qL7#_i>GQ!.T,(#T<7J8`+E!NU3:_'kS
Z#8aQo<bY7UX8%\,n4PU-]-[R(1m:LO7dlQ2EWN\QREgV<(%->KAm:`'$2>/97"=S(eTO0=!e>Jk[Fdc;gAe!K=1mVA*0r7iMteVr#UbjGhMjSDnj'WE
_#@&TGEpm'oD>OPgr@FkEqo],$=U/R(k,RdG)T#`ZcWH2U\!YUhQ<"%;TOI<;3B0&/>Q<eLb^B]0HFEKaDqkf?i@Z&B#%e0UF$mA4_IF5C#KmNsW2Jb=
7'-,s@ZA:@g_pL;@6a;\6PVb2):?3#Ji0">8AaR"B5nD5jm_X85^E1g(?kIXL48sdb#LjYX6S\GVP'3_>P6*B8paR?r=rI;a5\9j\T'eCBk<<r<*'iPI
_0.)bW_l=Q5lpUe/'-529rOu.Jo.RZ.,(Ug`M"m?M84:>G3Zr,+ga12aV.+-1E'+=0m)]cfq"&H[DPpYh/&d;b<X]g;KP&K1o!<ks+3CG)5;0E1WOPE_
Op/GZ(sXMUI:AM\+QH%$e;VQjPc96A&j3>5!JQl)ku;u/9=9tBTS;Q7!,`_YB<QR,LIXJk`*j^b2YaT1YJc6>Iu*d3BKu#h4Cmq8eWa<4gL)LG:=#\qQ
*c>G[uu-?c1#@"i]Xf<L.r5oCo[rj]=2K-8_WmQ&"``,^&?NHIIo`aHh_2*DrFrS(43(m6t@f@=T[Qk?h))?=ZK^[Ui6W`iT@ZI(,aI3+5;W.mF7tlme
h3UCs*R)Cm'#$`N]l1];&=dt2H@N;,?g_'Xbl,#`:0/FZ[kOn$-;]J,[GC_rS[fPRRma+`'8HW4N)@,['[DP+_#8qbd6agJ>\&cCtmS3@SE.E]`Sguoe
YI11sO[FaXUCucaMJ07Gu^?5X(9<e%k^QC_R-lQLqXZV.YAbfhL>]OfGWV>BM0/ZJ@HT'po_-knlgWOqKS7"6F9B.t%->tg]%@MIODZ/L*P>:ph5HA%G
a=YgTP?%KGom#F9l@G6Rhf]p`f\TS^8Ddk08H/'O:)t%q1%>_/.WQo#iu$l:AHC%C$Hep]U'3Q82+J8tSZFEqW7_PAikcHp(=pP-nP`k(!cJ)Nb.+JdQ
dTEiRVOXmeGdU2VY(<aA'P1JL9bqA!RU\2<.`3F_/kp[2VM:<?8j\>I_:'17snFSZg]l)0$dlepiagu'2NQG1[5Eca1h=8UF,u'`T5Lh;sAFDQ%!\D&#
9[U'0T/C1d)SqS0`NP=R5M0%K@s@,-F&E6e/MOe.K,h;\oTG_Wb#Fn&1_A)`Q/C)(!\PUH5:%"AVhuV,#`C<TVfB)_\5]Oa7"4k*m.CUFVN`m4#U#>2H
^/MJ@#aS\'NW0T!$-H'V3njX"u"2NY6OKrsRJWR)-u^+rNs)8lj*hqOsqQf+hgOm,JtL[b"%cS$?,QI!EeoFYbc,6KpA,1k-@L=&`GlQd@Ybhc6cS(D\
<EM)lg#;MQPdk9#R>;6I,Mr1mpp\9mZ0g9RA9OA0[Fe"OafBt;r:>Cj&lE!YiGC2EZIC:N!+ae#!m'LroirmC^%Hm_YKt3'<m9$G]]2!(?.bG3"[XmE)
1-dEqJPKQQ[eOlDK/7**]?;B<//lXG%r7[k])o8'21ILNQ=kqMD$TOd44C+&^cV6BH75Q>eGm&;I-+RVRq]I<V"g:`\2"FkTd*6#EAk2)rD9QI<L[HQ7
)>YZKBI?^>`pTg!lH^hfFs2^JC2C"#+1s3g,1:b\2kNin<.-I:ps0U`;Fg2+"3A+Cj7&C/eUTGgXM?sc:@do=fS=W'A2t>G;qM44-Se7MP.;B;O-@j`R
WMQk^*1)-^";?%s^3[B^u7'2fhp@r9`6fJeOL&7"1a8E+@NSY%n]EX@J]JjV'"3cSf\@m6en0\i'M-G,n.G$o5[)ZV:7TKo4ln@`JMr4LGW=M%e?"ost
D.i\V9S)U9^%/qhjZbOeIcAS:6$d$0')i[@21"D,K_=p[p5p0m+r;sVO]8jt65^J/_)=eDN.,pPPWSof6k8.33DULV<oO2oAqot9MYQ"i<g^rOdA0/ct
0,P'h9mAV80FER0-h1#:7q$7E+NeZuZ-aP_Di626l@k-H<F.KCQ?i#JDBD8!%4u%!tCAb[,8P]i3nql!KL"el4#E=^_"IWI#(e'W#051aIQZnFT'I6=\
8J=bYPcbZdMY(@;Y,?-)`JQ&\7AQ:5>(:7!44Xeu?C&#THJ9#1R+r956smknC,]hIVBUC`>+!7g9E=KJk#na\eV'\TbL`QtMb4@%eOqrbmnY&[N<0[%/
Pt^]4Jqh8cg<'kC2TE`@`0\Eo%7@n0%m=b3fRkIYD=PgK#esti'T%Pa@!QiQX$Q+hlC-PbH_p<jpWU[BrQT!+PjfYXmO`KOK40O>FdEcCg[9&\f+%1fg
@jS_4/spK1[Q@WY=;[F9@E!N,(eVG"@HbB'^<*;)Xpg],Kh:KPfh"\k468__l36Zc0D>Bnn+jZ%aQ#LS'B\YRr<Ar;,u:*r>&T;.fLAj'QGg^+I\W":t
(^R0fF6&DsI1W?](T#->:V?0B3e=>'\!`H'sIC-qu@'D)jnc/*^BS/P&l1#!G'B5rea>Gq)g+-WnYO7'jrh,&0PlDA3Mn.%A?ln^h('31F&5ZJI'',bI
XeoJu"&^hd88X\""%K$eIG5/ddLHa`7K`"d7%,LIUS;8S;]8_YBU*l^#PGstHicF]HFQM"IY1L)FG8/^DR#<!-ebe:>G=A?iS@J%jUk)-7"2sHME3cr2
K;Db$l_=\:8:(nENVq^O5E5Ei7EsXq.e$3+Tn*9N*.N0V7j'_6gZDC!DS20Vm?81t6IaSRT+l"<eEgW>0K$lnd#":WfLH;61Ta$TARAJob,X\`n)fT$J
CQQ!=HG.kl;bOacN\cM^UHE)4-_b(d'iW-(8tFTTd&ck"-Hi]^BY#D5@?A6GmBt1a3%S`S4mkgEYEL'7B@+f#.d3-*qVQaBt/5?L7p+gf=D=&Bf$`eMt
>6P0[`Y@b?$H:XMtEH2:&/3lm+:&M26)gVq</QqnBH7@ECU3BHnC$:>;B<9\jA,9Rsr"i,%i%fjkR`a((2`9-*&h33Z*&Q+a5$fb#uI>6[ZlfV3d5I@^
\2a7Z+.l(Hg:MQ*J]LE;F^\_A!dZ9XVAgkHhT)rp1<Zm*![=g':lXB'.a7')C.;GtAC2_YkOBE?Ig_iI1h*!hBR5@4O?d/BdI!]^.o5i=p$*2/jper@3
#RM%*^+d'Mi("o57NNA9lT'`(1++Mq9THbWuedEaa9SD[(D<$EC!-a9<pDJ(k0gc2`L\>;8<XK9h(ec7:8O.X@74_'a66/uP2:k*&6#ZN:)9\%Nlf>-j
$^RL5H';S8;7HBXP=a;.6B/*"42k^BAHoafD_d,E]g;o)Isk6OrsTAYaqH7Vb.aSQ5Gf;g/C+p>_n#RHjQA1G#"RTHX8KctWdG71m5Hm6D/-cuTfd,4D
RRMVft*,=?Xe=dS`I034>mG#F>N>JaFPE'eSYBXGthbb+51+n)cqQm:jc@i9p8VLBtVkij=W7O8&od.4McCGVb14@PZN1roOEXE@iA4'&[M!6q'f;$*G
VCNi0J;V[3HFVgAI1dg"XW[_3=NOS#rGq1+M*JQoH1[iaVim(2#RU12-=26]NHW^!iMgY<,g!n='.P#mojHmP0O,pD/)n0PA6\OnOl190#P"*6tDk!M2
,Z9LPk$SVNs$&.p,>RMfBc)f(6E59=s6[ikA(40jt;,KP]h\b>0ukqS\4.+_!"+Q@Yu$P":4SM*.!b1I>u%uc_ms#LkB^4ujq@o58rNT]NDO)=:i9=!Z
cUjX5@T\+W%oD[+:!Tn4C;n'Ej(F`BW6.Z*ul7:h`4ZDUFKJrKJI&4EXXe+I(*P=Y@@E]un&nqeo;)WfSa!,UFcq$7JO:>k9S?.rU?5TEaGof":3m`>J
J8n+Lh(Ic@l8.2QREsF*kL=CK@>.[@)j7K,Z_"#O8X[,7Ni2C?7[5Otqk#mU?21rX0nWJ[B(6jjKF-4ddfMt]2BGl$ap.](KT.M>80PF;FdteG?1</mS
K]$;(_UN`_CMB$IqVP%YG(%:7HOfU,=T1V1QAFe0*A%n-cl3KnuI!#*^Mu:PHOjpgLqAj)Sfj4qCN\2MWI%<a)A<"g*XkrVH3@NGJlgO1n":]CPMa,NN
M)]-^<(i];+V2IsQ)(&4bm*2OnE6qiWi2WNl383]^4##%A\:Xd*0H*u;jYn!hS80a3c.]Wa19TW4ek9o"B5^']jo<VFjMdfOh$!=dXEYt^*?R4u$=D3J
?G>>//.;d'=h(QuN&fP59\.Sd8GN<t\6'RNc44b4:,5c*SGMY_]8B_8r/%c"K?\aFjg!1*;I2iOb`f`\:mi:pU=^-Fq&CtPj\6t:gMecSF@FSmA_6<JS
N_;e,/PZLdZlNPFN8im^UnIafCl5.IV.b1%pGh>5I[t4hr(qc&0BFC.:9r]=EHa,jfdD>$f^_<WG\,E+@Qb?*O]a3E88BR=NVkeo"=VWPd-18(COC\_Q
bf7Re]#n"q?Ka7dL)u''r`Va&Y]'[aL^=&HU-o2a(kMET_po5:B89&,I>'mUrBe`]:::)AG:(Z#hXboH0*GUFDIPkt21]PAa>BCJY2dknP<SB)S*r\L'
:G"Z"W@0a,V[V,k5TLZK>eT''(qX<.Ipl9@7jKqFfn591K`'c^o/!P]7]<TW)t`ffZr[[ViFDMQK1t1EbL3)?8JMr&"@(^H#b9g>o8g#@YcJ"OS'u!gR
^pN\_`j,M)^tC+LGbXG#G\nV%51:'$ks<*JnB[hAr&lBP;8W^7oJ+p$#%X"GMJ#5J/1_5)'Ciqne.-A<aVnUB,EFq%7m>F;tY<rBc!'_9iN8=]G+;)P>
ID'"khGPACQ80n'h@FctkMc3E5W%iNJfMU<`dj]ael`ZF4sn_SYdon@ur9#i`%VZN96O#O'`^*'>]Mpo9G^`;T_Dj7/+JY8\^L3"oUcE5"7on]QG$uk=
+UN8%-h_rdD6j[5:eJ$iG&;S;pCjrFoR&/\:3N@f5&@fP:8(MjS$0.+kR\nEB%36'ni-F_:,;t!+IE14$OasH;\X<e0oJ$8J130PTq_f"=^a4M*q'hsh
lK(8$6CJd\@+XRXYCO<aeNN14^DE=Hm6bhMa8f>Za!OkGet=)RX>bT<7k)]GN\?QBUFgWqd?cmBHjG<q>aJMb<?$+^[i"RG^"H;)XnOs_?4j?dbAl_:F
os<NS1D9YojOmCKYL^sf`\+0%hHP:5EjbU/T51rX[s2">QF5QX?bC6'u:[%r+BZW.=e[V>c"WaLr+4`rl4q..oeK!E_ogDf3sF!2mY(PUnYJ;SB793gs
OLLI-4I(rnZ]5iZIL9#$tLS/*iU^ocg=5;0D800J(m"YDc6jct#sAAU`ubJ1pILl[APRo!a'>\2Yiuk;f&=B=],Wk]3acR3g`o_Af4BP`&ar]+:&PJ!r
$H3mjSmrWN&WJ#2WAHSHH;CpO)W/m\04h<J<t3N$'D6\*KM-LceQ8@'%Y$J%#=h>sFHkQhO).k5pnl!>uo9#&oFjsXofh3'sWp+:".VI(F@L&him+jJT
?+P'aM,t.o.<]KfZ3c^t_(akk!]jm3),hf"pqg.Q[htc!d<]YKKV?X/Cj9F!mAMVNLTa-hG=8g*CB9!*a8HU(LSa?D@"t.!X?+n:bL23paJNQc@<G,V/
LY[7cNV4;c0mt^:C\cG"]XZ+\1%)E[//4]5"^uKNiQ_7\rE<D;1--(F8guFe3Q$E=!5YJIP</B"/]>q**lG"-F@H.>M[]38C:[mLC/ToucH:eI_18UDK
,:IM^q@^%5TUuTc$+((r\^kk]3;Tme0elG.jHB,/'e1$71M+.&,g3hHFSoh/>lAiN)>6rgh>654.`WkTs6&bpjH<Y8p(>^k(9_[*/L][i(9&>-,dRW+p
<@4Q9id.V\*:'M@/Si&/&`&'_);$Jj3'eaQ>T,leu&IgC#;O:^%O7^bNIBXA)t:ms.k(o+9L=b7P9Ff:T=U-Q0^u:[fA3`1ZCCZ3gHnO"Y]HM\AKehsb
,a#mRJ(WZt)hF6\5ec_p:3d2Sof,lbGqc'QVZQu_(&&@1u_l$c.B85FSYf_AJNEbfF<V,_6g]\u/A\!cVtS`9+tUZ<<-/>``/<^LD2E(P/GnW0nh0Xt"
8Q.,(eas+F(NheMWQ/KP0HtsW3D_).0`Z4qVl0]X^)/Tgf=Ugh1-9!Z)>C5\4OF#2:f[iHjbr&Y-Mk$tR!6dBi+.ms]Mjf1gb[%A[?bfR;9N5n0I(1IT
\`c2k7DksSg@B*67FZ@_NPU%3oK=u362\fk8g=RRLbtmi9inY?0_Aff<bgX\6)Zfoiq^7$1DBH-hqiMtX\SHN,8@0iVC8E=dZefVT-+!,Im!H';pjZm>
H-1r^lc=im/()Gc'^uP]E2b>7ue@55HkUN@Jo0!dtKEUdjNYZa0"4Na+(#TIqEG)2sJ!:TCjGYN+hNK8"e3ZldLmAhPmC17^!T34`tl0]kcjt`!f2XUf
u";/h,lk1i-?T/r[!@Z-+Q+m/,:.64%N,J!9"_1q@k-j.pK?dLXH9!80q1;4VlNP='oHOt1!7O6"%kpp?q_Y]?#5"Ib)J3nA!+mVA>]#TNsBT-=SM)iN
ok=i7q_#E"Z(oWXFXl,NWc;`PS'rIhEtb)g4S??DT^)B9Tj"ZiuhFYd??Fb3@EO6%+W_H:8XC[Y6m?)$[0?AO:QNt9W6VDYOXaaQWoO;45:Urf43Y4\.
eltngN03O:[fWb'F%kcc;I#/,E%aM].7W^.=d3.%NR7RDq4**FQa\LOGiCh-k(Zis-.;m1O1@Hg@OI<O`"+@Z(Di<)(dohUT$HDP_.>HYd#04tSZ8Qj,
LSP,r^EPgh04ZT3Fr'$aqKg)tki%h!d'i&RG&Vs]ImSTgjbXZ,@6(>VFFiH6I!]P1#Ip#^rh:_%&%8Yes$"FNg$r)+0=3f:f]dL!0!:5f>]?O(=KM8HZ
1GUC$gX&qQr!Z%80\1n@^g+?I@DE@']2@lK#E"*j&LK"]PFk#B>fbeO*bmU+O<^46666?0"k@;j/f*-qQ.-)+Bb6L2FBCU_BE+lfArZ:=;Q^t=sh&?"@
L-L;JV$W-J>6eBYWHqT]\PfOX-Kq^@IpW5GGfP&a^\*TC-mPC,pRWnarY\-L7!^5cs%OI1gmJ6kms/`E=^<O;2',_Ah>t8mslV_Dl#_WnUJ1c$G=tMhV
Va?cBR#O3&KQPlK))OV^4lEP;I^Y"1N--blPE*iOp2aEUt.SlZ%P35ES-(%("&*ZVD$jX5P8-TM,JpOb,PBC:;2'&El0TZ:LsdMBGkk1pX/;=42?ds=*
^o'*[8GYd?I.C=Kc>sC)4^1??I`m"'57680!No7LO`YAQ=M2ETR.;rQ4>p<o@B-r)M#E?8BD4%QeG&!Xh,!V>[;E)N>2Rq0:5Y4IlQi;<maXY2kpYs6f
l$D/pU6okoFP],'e0^fKFa3;K]GE9jm_CNmAktN2#LKFQEnfrj[E9AV#br;[&a;g"'HlTkb,emf(kpIP3:?4kN"_5#L"S@QTJZqTGunq<#'&A281W1-D
`%5\<?e5Y@;K8SR4a*@/mqBX@UG^<(rsFpWR#ZUXUU`^^f_83?20Y-/K-QdXo7Ze4I#K-'l3-aD?=.`<I$)jpmtH;2Es5sa@KD;K1\M<bZu_$RfXLu&,
WhmFh/SJj."0VS-)?U)AcRZgjiF0.6Go3:`KSndjBJ7,k::l?kSH,Fm[N7m"?k+r^tKrMMe<.p6nd7WLE.hbr/Dcpd=(>C6bYs@bDOer5+24&W1-G.U/
R($</K=8U1S?P[DGfq?VYR\*RaN80Y0\4J%H`\o2j/U3.Ft'9trrTAO'tl%'>ila$7.B$H@R!>P\#Q3*R&gEf5F%XbR2AimBrXL2T"Gg#d'f/E#Jh"%j
4!gDL0c(Cq]_T7cL/=>DBiO+Z()4?SMnU%tMf].R$d%49W$(%J_QQ!;YjHF-QQ&VIVXphR0MA=#[NEiIJ]2;r/1YS#c^\13VEDgP;1MdK>Y)9NXH>*-N
G5+I!0Lbkoj:k+cl1VVG.]a(S%RPSNQI;/Ic/47@po678I8D<U4Y-Uidle;pBYCE3f46Lp`9lQ5UDcklEl!PSr0sB`/?<CB/40T#ZdS;oAaRDoAKMkm\
F<"Nj:"qITdf)q]Y>GZMD\*8?)WL[QVcAR8#'*a;k'IL]YX[qY&&H$TT"J0&q\UiCZ`30<ZR2F6P$@.OmCXq/GQFus4]O5r#S,(a(X/gDOqYR$KB64,f
OKWY:Tnk"(oM;6jnp_bY8N-FU$>^&cC,)0J(P%2^DOL?,DtY;5:=eeiodBLeMIE*E\if%-E\(>#+uuU_.jrTi4dqa/QN?#;`^&6`_=VE`TCDN>Pah?2P
Vt-hI/A!Bd4P_(W`e.&UgS@C.C2iDd+:,L"(YJ+*c]'%3fVIUH"UdqJYePkbSS7Y^CnQ5&MRNbu'E#b\q'c)>::p\0?U^#J'#Y4IFW65`>B:g`aT2HL?
=b@QSpOa5]RrZ,:o1Y@>&N!o1ppsr/'-F>kAc@6#e0FQ,Z.l%2>\$"o[S)_;iHV53--!:jB5i]o_iupI]>hcn4$BrEI%B^I*;MH4AG!s8d?Tc:B)0\#S
A\NuFW`0prAQT;;iI[).nZ(p%b]/gi'ba&%n?[g;,as3NbZJ@`+Mb6;eaoM'9u3<@+]2)A7?d<5Mm.Sg]8iDAqTc'L5]AucQg_KQN)#aTK_flA#e8!-I
?("/&dY3XR6tO7hJ;C)"o'JfclsH=kL[$:aW-Gg7#2]kd^il9J&if?;GJ<Ze9VAbi&B[UkIo:'Zo8nQ$)[gmMd!-d1Q"D>Aq%-?(kS;Wr!lPfgNn(LFa
u2f!sI^hAn2h+&BL*UPP,$QePql33ot8-D5%.3"%X/-[_"&aQ8L9%nm:,h398PZ".plr,-S"MHb#i[RKg/8+Oh0X<?O=Pa6H4sVmpsd%,G`n`TJ_FmbI
-Vg;=JbOupa4KJH/dXgi\pg.Q#^pEn63-Tq$U]I$OS8eXa*d+;Apao"\C!d43eWU=7CS738s)._P6.M+!FIa2cL\'=pQk'0sn8do=t_4P0q/f!!W]#7\
%ZrlFrXcOU>21L.RIg@;oqLYG\U)(J\4Ws;ICe@Cn%,M!X\L#WgEeNdNS])5`hoN^h[9L0NSdgiVp%p)W@?ZB(qhobi3oIh:HdY+PMUKkOg[h]p4Q,W$
5M`9M([1s(T%LBglQ*I%Ii_,)/5ffFR^Bmq0h$=!X)>VGW!LHrM?1sFG"9+P<c8kB_:8;N]\J+p9E41G64T"rIE!,n>lJ_pUiqI,9s;r./"4i=j`J-TX
@aR<.6N6FX^h]BGUu316KM4i(?7ne@dYb3LI>djO9LmP=Sol,26/(E2gGJV?A'd=\?P^u+7mm7GdJairIBV7.99N3@or`TKXmo52UpRIKO=rdlh&MiIV
Ys35QB3RP]-C#Bn30f?jp"(jYqk$f&Jk*CkR-H&/jr6i`DGrVDQ1V6E]e4g9iqc9G3h26m%Z$f-I,J>Pq:<H*cgqA_I6ZD1Cm2]F`Fl,P:ks`>ac`)",
tDa$5,U5p=%"fgl)T/a<-hh9Pg_%`$,^LVTiMm<%=]OSS:oWh&D-.,Hl&/<3<DJB+#8PDpVn+Gh7:KsPR.,9C11Pd"Y9%(I[<(FR8hfl8&oG!)[iPL'r
?PQp_4XrauOZp7tQT#;KeCd3`<RqD"@ETbuY3k.D$[AD2t1_>*EJrg'S]\`5B0#5OC9iB8"s'peBog+MW!t[d[Sg4jWm]U1A+%P9YLa8@6%S/\C"-?9s
!"GkFQEA:BR[G,b/@5ZM>`O7@G*CWoG;qH\&e?<%HVnp0S[cr6a/(YPRDS@>1#OD(38^eI?0\2%ppO-tIp:H(E<(_d@0n"FrE9XEEfO^A/sbkb+[<Su.
JFGPi.PtO6-@(HaeZuX9i2lo'>W?fB[]QHqL'>@<EJ:]bE-nXfe%XF/,LLFl$AeEbQI+KSBV=5QA6naKF@jY4j+;n=^L.4-`].=B/*!H.#p[TGr-R-H*
&3&"d6+8POIFKZsaG4A4:nX:t,YiA^"DO;XJoHCB\iTQ'jP2S`E=$(G=o)00O"ZKpV9a*cIn5?AhA.H1GkjX5&[E=s)9:Oc5C!R,%qIaob+:Q+E4,JT0
#LB![V;#ISkHA0f)=h/A9c2"U@s4t-QTk<2mW2*K90bN`Hl&g.D@!cU_]P1/-.#/'dNX&*!LgJ&].Egl^0^%8t/-=WOfXE+<l@7lWg%I@#jP&5[[lj:9
"Jm_o#K.BfU9im>SKVQ(qS-4@G7k,1qW*-/)9s-4%?0Sq=[(p[ja7n'L3\TQl4EG:\dOX-=c%6Ms`9uV%!J`FG&c#?=Mq!C+HZ:GC[-O?PV#$R1X3W4V
SKK*#+&L.n=nDOV12\/!MV\QsakB27mnL.,dRNpiF\XsCV;>V,`Ik@,Ml-'DgjZ20Zll)&3^f4X^R[>f^:Ce>iGE"CVLn'g.N)cDLWLc26Q8iiH<7d<7
1)iRnfKp^NW7k+RfC?Ii+sB&k9<O(5W.he42dOP9VNm+*n9U3[Hm]I1RIKIn&AOb!#^?!j=eYT"D8#%<@uk50[.[.\pX,Gp+4#jCQ.'HD1O7A&KVu-od
^Rc$W$U-Y24'W>6ilLF%7b03I>_4Ol1^CUU+j&*=(kb_fgELS0[9>F/_P<_'t]T$%%Yq$kK7=@<?QIc:Mc-:Wr@'js.M]2g";\OKM50E=_[6Ql>1jcHn
m[\F#S5L&O;o-:P9j7$C0O_g<R30OSYOL;hNr-as:sW3!5P4N;'0.ou-iWZk^D2m5]b\??=W@(a;r5X?Ea9QHAb;i9CH'eP@(&m;mIXjJ5iP>OG=I&8n
VXCXha\i]cn>T'MKj+rOMJe[6h(4W]57X*ND#k@</H:Ger+YUl@`\Z;mn9/F>111qU)3"ISp+uCcM!J3n_O=`5JJ.kuV@d)8oaA:"Rp9!e=VkEQK.qH]
kjd@hN86D;S])H2G6fEHQ/iX_dE4VaIp0JFXq!7>U4[VIl"]2uAT?0dY*KpRe)m+_"$5d@&U<gBPd/g+nWgd#$K=95qei)%R>l/o%3M0u5#c:8jqq_T0
th=i!oQE,CH$\57J4fXe0qo9_)YeY/7g4?<-\4Q6c5OW(u=CFgTVE`Lr@&I,DJjH`LrV!J#$#RT^W)e@n"h%_XZ"(1^1XIDH.8nTcuPF:n!0H):N*fdd
lu)<c/O1+0FZ%,=_&IXN9@\ce#<q>)iWoVEje,*W9I]0.a^OUgI.N3PteWCCC),+V(+iMk[_"f%,Q.FAsMG2ulkS2!Sur(W5XYPW-gWU.eYbpKbs;C?;
gQn>%L`2A?<(%H+W=:#IQLpe%gj<BO["?is(m3rm+\jFSR_'EeBu`ZIS0<+8D&'%/=QJ(30k2?ikc[:TVJF?2+ID"9b\A#iV,>n(AAfE=Bk;GU=l:'(Q
qqG9M_S=GceXA#[&GOnlk01A$l?*42:E^iNmUl@g1X^4sI'#_N$qu/^HnXlK5<iUA8a^"J$1i\\+0bH!-[.YUmm4]&!:]Uc3Wn8PLj3D^I+@Z)e-^Fdg
cUGsPO\Aa"6ZLIaep.%hn65ftb&3!U+n6$!??.m0T<7b)1U=hH4nF#gJ3RTeo,@]P\kp*#'p48PC3J7b3Du-n0$6O16Btq9$l0W)Smj^C#<k'YdHZW!!
,;aF6jo<l:0'j<5riL`M`Uj`9#h["'Kt;R24'CEOo4bfp:f!>G.BK7YAM;7MCA5>6Kk'(D%M=PJ!t$nRUnOu7=VM/=U<$JkkrgcM6aCu?Nh`OR"d;q2-
j^9"PD]lQrFCr9S@];=tWZ5eCb7d>j\p"HSesIn=rF!jVBoGRRh-=KIR4!YB,&D1#<Xk-8fTTbh$T6Dlu6)"Qah=q`k[^a,:_9;\D8QhW^207pt&CDtM
lJ);KWgN$X<#qo!SKJ8"!f(_7?\)_6h])\^H!cA"EcQ_K1_IuW4Sp\A:KM<b*l,LpE+f8g0/X(_k*R1BHH7qu:ND.UtV%tr7C9muM@?An8^%1M>8S&^)
`8&N=C<Y0p5%8!_RTHE.dqm#W/m523u9I:eU"*IHUgaW+cJ:$#B''kY%Bd:;MKV@=$D2n:20`Yo/,oitl4uF4R!O\'jm=3$o,.I)hROV;bFDSZN^$c*=
ZNN3t]2t"E/Ir^?dnbg%iYDAnCMp;.0l*VN2BD6k,uKu0B2I$Yrrol*k#[2":ui<qN"%]MZ,7mAU..=_U(Ht=H__p,R6s_TVF!4HF9T]0MtDWj1$rogI
[%_'HM3Lb](<lC5@VlAE4Zn,]Zft#iFn*U4,,.pA:]#rIe?+gFO5fNLq0+TkmlNcPJ&A/c,q;I$(,jd(K,CKBj%tT6JkL^SGY2GA*ep:qNTIiaPiM9ER
@*9+OXfao@T(DLet0(SX$H6+j_#L0^]F)nqbg-JQ]59<kUSqn5%E30#m=QH]m@SB4P(i>e*Ac'pm'a][N`V*PP97\7kY*AfOX9MrG1Ng0OC?%a=(%T,]
FRr?fk:.MaIm]L5H$OE*>*m5%j>;^\VR--\MNj>7>U(3m/0^>&Vl]1C0M0rWj#?0c:<e?hj,%La"T;-B-'=M3_(9<4@03D@;0^PCN\"+(CN#p%!_JcnJ
GDqpRU.!@i#WgUoO_s)3<UXFWOVlQ+c7rKTlPrU.R"Ybtb&HQD!OBW$a*I=!5I6/X&;n:D68u<0<0B,ud\ka&ggl=KMIHo+1;iFLWSB#sAk5Oh%@J7TR
jpj0;U%N2Qk]lRF(H-^\kXM=<+Fr_53nnE(IS30r2@"At=H8l`Us6Y@0m<B_-!t?Tf2M[ZJ]FH#_cU.N'M%^#;+/_.`7lPe6lQ.bPU%fWCXd8l\0d[t1
a$@0;SGb%UuXfp0KU$^%FE1U"n^(;V5E*VSQVdkQtGF5j,ioBeMDSqU(:T#./?hWgjhs1#1#m:*SG*Z6Z!td$oCl/p"kpE2C0FkO4>+dQ0=NCVunT.$H
+;ZatBmZ0;\!$9f`albQRq"q)'4D<Z"gQQ=OkONZ?mC][j"V@T-+V\^BS,mWsdB`m"X!ri#!<-p3:W4#ehBGlbl;\Y^hU>h&<(@Kmg.oKfsg:Bbqj,X%
.&%2ci44m-G0I_(^6kqc>7UXHX""*n;N0V^\s0ZialE3ja>pkZ%/l,V=-#cn\r1FZ/"+=8XjDJ9pHs5q3CU_&-Nb,ZtA<n5A%dd1HATYbjYAcEA9m1oE
+V1/OP%@KtNh^qC/!BqbN5!->)k35C*N37;[EsAJDp]'_PCUH9T"HCgIOoqU;kQ[ZEqbb9@9mP\cb@(DU]RFS@U>^OdR6jq0"D[-tm%eNMNfeH'I0j]4
Ou&ksh2P\!>_:f]iH?RiIXl5,!u?XJ$DkR^Fe"n4X=1CRR9IF,#V2'A?MdTuhS-Q&CS&5=4T_,4XoBMF0"F:*jY<<-aklHGCk6hjL81=5A=KrV<2('fR
a6o\GBkah7fW?iE=*3;;`b6a*qdiSRE$DRei*t[gXXLG1ONffDtk>N4%&\+ci@Z$@Sf_'@]pgW!MI9c9=&hEo*aF+X9Xt,^sjgZk%044+CT#tSf;,$MV
>ph@A.'*m69o9koJXYb1SVYKj-*`IBI,g1CjZ]eF0ilA_Whf&3$h8>!Nj@@`Mf8eNu6]7T`tSbh&(\n7gKQImF8B-"D!s+;WcR"=UY84D5a^YW91HF,2
d2j/;TRALato^0Z4,N@%hU'F$"=jgmq5M_!q]N'aS\n],gk8$p;;r'G,N`4q9.X[J*Bk%Jj*EPGWg9JtsoLB;X3-1hVEr&MrGfb]%9"NZ[d3#S43W5>]
2TXT'rJt2":HMIS(M8MbLeAI)-_Ti6nB(kR:cG#7LP+p0"W?\`:*!C`'1o[LA_8j8ZV-HrYK,)f'])?PVR\fC'#%6L,45jt>Fi<h]ZspC071]>0_1Y7$
E&AI?AG18fQdkn8M<!#%Ro6AV(!g^"4.KL7"mUGJemm285dC3R+@Pa#--OI^%XF&AOXMhE^k:$%s%so(Vq!SOIsKP*#`rtO8SC)6'L1feU`@jH0LROm6
_u0[_)ok=i(>ibee#W?lWKWDA?1PF]5a.5Xm]^:;G+_*&^M^l/VY;-r.thL#oJ52i!nT<XE,l1[:<uL_4>@F*!MnAD4"I(=QpYK/rp%.B8,]7)77J$"L
MI_EU\ehWSr\lc$*WpCh3DeV$I<siu;s%AQWa`^4Jq,PhJ!J2&:Z":,I#n<Kh1V1UPftKDsY.6W+]m_jFg@l3eJM!5.KdRYb7;=\!qGP@@9-!+_e]c'8
S9;G_NT*@h)*3F=8ee_ps$=8[.Z7smX[P>4-Yqf?1,kO"+\nSjsAK-umgW33'?,o3>,g4EI[F!<aInP@A&O#]3e0,i>DbZ&SS8QZ$qC=r3fWV.i7,lom
#@9^>`80s9`mrVrgX(LIU;MMR6G_+JlB&miu*\-JsBRsL'5Cgq"!X=_UD).(-F/6qs\;Dmmhpt5AJM+LNC1;?F]pUf@,])*gk)QZ)];Q8e3pX3@6/CCi
mn-^_^!'3)ol3&.8M;kT>Wsqi@gbY8b2*DQnpdc);TU;rT:ft'(r&$QD65t"o%g79Qje+L?Y\IKgpmgnQB'K8A)Du_-&JbQ:sftU7\S[@d7^2S;V+"(O
SD]<0re!@_=NM,_2/'Ag#Ki?dHCEui%;h1AjE3cAKS^:fRW\b7Dgg-i8oTMUrfr#=t.ro0dYB#^VN;Rg,u^JSlf)&KE5KM_mnh([YZ/t*Rq,OE4tTkT'
XLW%329j"5qUi)967eH:"T9C]0ng#0Fi56Fg$2]->j6nBo#JkE.,1MG1>R8RhTq8^oMM1;SM+1sunZFtcB*LS]k;b?DJH_g/Fl51rOYXsiMRB!S]i)dR
#+762b\KY!La[k/"&*+N17=UeQ\c]/$'9bZ-J(9;r6K9]!-j!&uOc\m'7^*7;_3scOU4t((&XCprO(s")Ohs5:BP-GuQ[0A]Ke[@7%nhEmG0FeP8aZ!j
tK!mMtUlr!*hA,)85R=5(9DLRB(D&@@MBm'L@`4A0?P)!@H5S*0MoRF`<g$U4GkbPmW]ko5hBl`*p="qB^+Mc0-)jde[i5=/I0HpSA=8FFV5fYQ+E$U<
BghIPWOPl[QJe@h2U^M7%CBG>D5lJp"sS&W-'d)@*'n-<h8J0K;N.n$+u.Z4Omg-)0TkU2:RXEW*Kat/7T*j%SotbX0qai2Sp-d`=2Y<u$H.YnG^\p6:
E"`#1$%(uL'8E%QqKdG^:_#d'ciS`i2!&sZc:!C#kHj8d=5.'@\84Dng''#BNp?UK7FTQE)`l6kX^r?:(U0=ba.D!+J<L+s6.==dj4fjd!@b?4Z9?djc
8%U.M$D&9EFL=>dRQM6R8JQ3\](I<1gB^Jm<&jJIL;7s%O7m>UY0mXO`e+6FTeil*:unrQE]jqgXIk`FC?;&)5Et?WWa!i+SK'r-l51mkQBG^+kScpe]
+s/t45+:I@bDe`qR7?/\'M"dt#2X$Kcp$0&lt:d[W%aWLbd4QrQB#l\J*EFOi/Q?07f?-blaW6uM[p[9iDD<SHAptI+=$0Pb>V^%-\PJI,#Ks_;q%O6/
aI8*LXW43>>:c6-%n&WW"DhQ/s5!:d)@u,WNPNg<@c+A??`4iai]9[\PjK?A*1*AW:@r5F>>LrA\ZYe>$a&W4Z*:;.TptMGiLkZ.(1p%$PIpiH5HN+^L
\j[/V&*]01)BsZ.N[D`/]b\&PJpBW<[b6]\Sc7@6D<DCBGZ@JE/&727Zk.hKY6Dn?@=G/-0:2+j1Vd*g0E8(rCmFBFGb(c_%a[*ro7Gl"d^6k(\>meKi
r#dC>a[c(VqA`s;`JBM7CJC!ULdtS1QWhm('REX(!_W*KNA0\'^65$^_Hml>Q/V@DDD3f)mhg)6X>2N;4H.J;^qe;d\._Y=c,Js:A3:EX3`Fo)nM-2?3
GHa/d$@4:Io=eS1Ks(+fQqFLM;iG(H4>jY'H--&Rg63R&].2=eNDU_0`2fNuA-D8YCq80-$>i8OoL.(2QFY,,')B:GR&5Hmps$mlF)-(q!5NHK0<fplm
omYRHE6KMH$cV@Zg_B<CdK>,B;FqY>nRLcJf.hR:$YZ;L5lZ\SE;!CGL8+_neN['[O/Z;ZMBMB/p%>B>s]_C.)@+(.;$g(=JMG1)I\DM(p.#X(_1!XCu
>Tuu67D2Ep(U\&bV++7R`o,]7bo,h(rYI6^JR,FABM]"Ipg8BSk=+p&P)89#p#l`4$eA5EQABF.\BX67(h?,4MmR0NV+'3<YC;Qmh9(ncmA5<8bgEfNg
6P&0jcPmK@M`rS;quX'"2!%muJ@Mqn%'YEaim_dPoo#20b+Is#rJR_jMUp08-lKD[\&lP^%4^cg3@=E!>1ds_*htEqpO@:P%UNnS3`SJbCV8MS9-AUf0
rhML%HW,+JOK@Mgnl6oK]+sKSc?=[/T.+?`DLaLhY+GfF>GHL;J,CTHq<rG?Ua1_"\h`X7.IP:TnTR]FrB^W@s%h7$$-/TUt$rH/d?Dd,D[tc%,Tcn,]
*XJFH/E"S@^Nmf(Y%&oV]"[h;TcpTUU?nC@-AK$Y'$#!jga`^q$Cjs"3?K[8Wmr7$%i.U,pfG8H/=RBId-KMGf1$9+)@iE)]5d%'PQEg]Iu.k$7-m)YI
t5JY*BbHt%XW;"t9C3iYpBnH.ZM>%oG6?t/K3ku;?k2cjn6:u4clhA`n,efHZlMbLV6PkM3JJ85PE:mM7KFu-%uVe!TV(hsWGMIpe`&[=M0P%2E`33NL
"belZ?XaQ>3pts1cF49QV_k)-\+gJ]r=+;DqZJ"fqfNX##nc_U@ZB`!S*Lec77#FU;$,un[h(DXpr'><O.c@6aeXIC<8dqs`YhfM8du/e6%$*m,;gcn6
-OdOD7L.Z%$3X*h3iKpS0qB?0^sQ&_kQs>-Z/.LD?%DQ(dCaC6/<cYU%OQ2VSK!n#3\js,;Nr;bdcV76EKkE6DVr&RO0Z-kR`t,R/=7Z)?ku9N]&RhF,
n2bCdif2pWVPRTd,h$=CNfg1[FGc8LfqlH2GN/'_EX:&4bM0`fO](=4X(J@Sa??VUC#k1]=_NoANG(jipjr;*J0J>*C$/'U[$\agqCX1COqs@3Um5G8B
Uu5GZ]k0/AZJm!!0Ql!L&cOl<*I!Z,C;P!WW3#!!HG.'''
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

version = '1.55'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-10-16'

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