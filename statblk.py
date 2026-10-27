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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 56):
		raise ImportError('multiCMD too old')
except (ImportError, AttributeError, ValueError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE('"=7F>)aNi9BGja'AZWLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh)]U<,WTZEDeSe:(YNb%NdN`;%MLm
ps(uYZLt9N^(d>j;?gF2fq.JS8E^d=!D`Sq$Gt&.k_&Jr(6<fc-."_L#%?6QoJ:i3GQHb>?A/=XqGZdH'Nu>j"g6i-cqUX1Al)9;U'hMS[PsbB-tdCiI
VVRN65*?GL<kIO7Z(I@QtT7--6!gZ@"9F@Y4QIP8RIA*-bdk,+]#R$+La,Jh\<l'=[)FCUf"DiJ;Y_2E08,M;Tj[Ld)?GSu+lFqq<Nb>r(RsY@X(sYW_
C-GV:'QhS:IZ?:cZTrM*G,>%^OcKH&@qHVtHo$?LMYe1;P8aj6@5@[sK+i]>CL)suM"O3$.*^0\UhT\4]JKN:T^X6gL9>u?1fbM(qVR)BKB8MD@+[Wc#
iikSh2A,;C?r(#<LLFi@$Nb[-9gKXJ:8LY2t.:KZ[G/H6D]JtL"hr\1)Ms5fr[-VUBo2EOI[5D75Q,6,24^DrD#CJ999!XRA71&G@ecV(_Md?TRIct41
Brfq:?W@mZe>[oNO)#aE1(bMm26C'n?+lPa)W/%X%9NkeU2`e#rt:a&!j1")ZAf;57PgLn6YcNM+Iu=h.^WrMg:&SK9G+N^Q*V]C>M10#(@oL!e@^M+P
+Qkqd?"])EPDoOI$g?->]Bmpa*kNLD$'[,Cq3`An#*BDFek5i9@IA7MP-$Y1Tc0Q:QUl^K)m[LV3D)3/V`bLK8I=T5gQ4&eAV];@<]\oZ(M.aB?lM)0=
orR+;PlfWE6aqN;DYF?'O<=XaR(cPU8EtG0'HpYeV-C6#k'9J.HHmpDdpXLi,dZ'se/@#2qZ83T+D`_Y?UtS,9!HK\t,&bs$U7iF[!Y7]BPJ#fX#@X4n
8^e)Hch@YjfiEmL+%P>TtdaA@ts_nX?S\DtJ2"GeD81olk.XpdeSqNu5c]3TK!?(5LXs)QCI7p-.?)_h=e,UYOD45MJC-p'Ap,?,1-RAKTMW_Kp6Ua6`
<pZb1J"e?O[/1MN<a&s4//sfhA7C^6$R75)TJ^E5VE6hWCZEk_.FmHYZ$PGNQ\_?qf+dN?.E_[C4:cYd.8%d7CRae:TR0S0&lnt*5Z"C&$>DGo_(3Qn\
LcotQN[e='$bWF#S^+=n\$7BYQg4$"9]2QLd(+G9<l2`m,46pB`s4s\cKqi1:>CgZ2!@:t<op`"g,,9(D)mKCLednp>Crp)''%*QJlb^@dpf%n"dUlo@
Sc\&BjV-MYh[H4Hc-9o6uU_h@.4?QK.5-(*j`?TLab$&ggn_15G;`iptpMn\:h1U,2\caF21VPcK?:],?ceU5oOQ@]%/,k<AJuT6/X8rgX8\V[0[u&94
WjX44eJZ?Y(MN86e[8QY4/eAbTmZEe_GG$F:/)^%>?uqhoAR.WC??GU5UKG\h-[gQjmR"@RG+D@CUSkd7i,FWD"L0"/QNcU+3Hd2A0JU?7cGD--r_10H
NmR!A2]R;Zh-haNGX?g'4o-uk?MEK8M'ZWTiE_H]@!bE()ZmFe<!NMO_BCn0cdSkE>BCN]ffSX272NSe_.nf:%%#+8:5h<@4`h8:KnVCE@IWp\3`^u7[
mCZ2!fAfdMp7.LrfCBF5IiaNP-b<iRf6/`%!UW@fqEls\*'Z@?9Da68;qm96./l,6*[]eJU+)TV:o'S#TeN7G:6H?@&-'EhU6?[2RmHS3,jm01#hB1d:
-?V)?U?Irm@auZKqD^RQYQqJ$S;RAg.A`.T_EYYqR!aA],QTd%X@F+#+7c:Y;IL9)KS3NiLg-nZ0%n@nYe.uo]03df-ppC_W[Hk\[K8R@BZc2j+DhW'_
c)^KI=)Ke@;@-Q)6uEVcl.oEq3h$[UL!\(]@SOar'^S[m)N!L[T[>I:$aLcJn`Vu-%44GkWD"7$@UO&fu*l:32^c6@"3VaR'ZUTS1Ko.T8^Z.IMrf=:X
%TD(:Lp3r\IFD`]X@"YWgJsh2Y;$_m"!=I_QeX=;$P-J)Ben4<;:FqZCFFM](W>4aJkPJi"Bc/1teM?gE1=K@<)%mW!_YeV-Eug83m<U<<t88^#^u*_h
4i'SAAlHKL,+(![3nRAEn7(9A\kMq=<K[-^_qc`9+&2o9h:=>7^$-;M'25Z/I;l:(BlZEJO.\#pQ&.L0@Wm(Hk7%."3=pZlrm0E[<gjo6l%GM@_)3f7E
RPic8K_O"E=&10*3(PmO'rBNDJ*spag5nCM[s)I=87m!icZNSS-O_KMMPW]><Aj.;pgsOC)qM2Pqa<7r5RU+ZLC.>HV+DF?I9ER%:2cWt").K>P!Y@V5
k`DQTTS087ZU>26Qk@'5L&FoO1]pB6a9k$2KB_TM`A<=KWc,@$YKh"NB[J$='6oY$aRD#//ICL_)E301OMatc/oiDJlN#7c$ap[!m[pLinmtTV-)>7=F
^Af`?#)R8J/hi)ZX/YkG__NXmMGBHZa5FrLgJ&K`\pCNM3JSjP#"4LhGE#.TC(Ako]1C10dpf5^+@)/3LNlL$_8)m@Sg=O3anSV&-<2W)`PW=!4/9\%N
/2q"\Ggge;oo.UH<cp5JFjtI?-HV[,WnNKlQ_(\K4bsK+;K@P)I4&Xqr5;k.AM>5T>9OD8.g)3pZBl:b4H_s7p=.d7B$pPS;j6&)ts7&e$%hc1"U([oY
BZ@qV'`:]DV\q*kJ1[NK-M"<="@1_(_,Ym4_3AKY`0R8:UdXPKEu9f;*s$;6f5NU#HCK$<mgSgl3_\#tl`6=<NW'n<+Md&/gTS_CiT-Cf:6)j="%?\Vf
T"6qq_[_JR-4d5PqCo;ATaGaOVpO;#Y8dN`_'m&L06aO&1!,]PHds3!9[\MFngeXO3FqeiYT`joCeJXJFYa?b'.\"E9rbSO?Lh'6soWF'UVZQ!;D@>S$
5&6(d!m="\S);n50`dtW<oH_,5AS`T9-_8hWCT:hN9:krZWTR:Qb2,G^tV/6XZKcPZCk1acB"0<\BLlNpFZ##`oWqBP*;[(p9L/]BAeY#?-Z^`TqO/f7
U3WVk3q+MA:kT._aS*/#2-/O'l`:SbT=lV@Fe:Vpg,:0ehSQ30DJ#--``]U0uVPmc:YsU3T,onX=Fj7bP1cpf4]KIL$jpf@DInAniK38rtn&\OC$>?:]
e:c:^gT?6Xb#FBDRBNZj?8=H11\L\S!gt%V\[]`dMZj^CpD1.Oe$=V6'G9eC->BfGfm6YW#48b^._aD$:=U@^B&?N<dg8g:gV*DoJ,VjQS+kQ_,.gE_m
fT^@S@$fbL>r;HJkpdUui+qV3pr#U^qX\15Xl?SI7<[f(u$]7A<uX+H6BFH)s.i'"mN#geU(9)(R=;D$odosIO"KBM]&[.")@?h!^2^OJ!"V)_aLaFW%
'?uY.,5uo)6;iVLGY8]^_5"i0.-hu:[.dt6qO>q9.l(#&ALR9kCA+UR"0/1=!=,?1dhohjne.?#Z?n%#Ncdrh)JUU0'Y$M0&P@<2C$GnY"30Z@CZajDm
LTd!uk*_2T3l6dPK*D',%cGR_1PbnBkBLQNI=:J:V1YQI@l43SC.6QRCal8tHA/N6Sm-k0Vhli8;l_"coD5)4Ym($5Lnj]?;`'.ZI';`DgOeL>So/%Z?
i$TP&:.IDUW@p&l2?OC$<Od_JEQ_]iL+FB)re,K##QbDF_kLF3pFuD!h'-@@Kg$OVa&,L.Cc;q#r>,FcmkM!1ZN)V[4M',/0fhD\RkcV)c%YnmG[RuHK
tP<3I[WUf]hQn+nHh'r#jl9d0:RfgJ4&i)en.u>e,$N]r*mU9u9n#^ND/j,KkOs(pZ+e^o=.2=Vr`nr\h>dfL8ks;@Hf@V#`\4r=52'6]\4N:c`DB$I!
kgqXA//7`dJEmcc^9[;t:dc5:LGIMV+fc4o#<'(2m*<PJk!]%6NChP^$d'%;*<(AVo!kWACdM+JasDcedEhpm=iGZFA.]>foKOIF_`<UYnlSCZ"Sh7?m
9X$TtMQrbs28IO74+Sc9o#o46ThMeHubQ51>5dOpERB=,a5eI->f2NG5&4r9YajEK#%YQ0g6:aCrCD&P[-l7+]POH3tr4rrJ30lMk*adC3hCJre_$!r0
P'_jC75A'fZ]p]VM0%-3V/K;&ME9tBA^)`m<6:-._GM4'ZD;E`?$\pnmof+.5N@5_*`n>_^2f]r:%VGtmr3eSac>n^r53iX-5$H4fqD>+l`CUO'r1YIO
8V9Y,>^j=U+b*E\VFR_)A"=18O0n`g6ca@*V4]HJ0O]t?=oS<o5)e>!IF:CT9mPKMi[8q":m8K81a$\l?^cOjmGI>m7l!l4mV=3Vfb`sBY,CeXH<1sK?
10`fV[XYa.LWVl3O$:"Oh)=>&nO%R2AWV0$l4"W<YR7Kk_6;1qiq.5[^%T=C(5K[BZqoY[1m<YF%etUo>Z!ZBk:u]>p_9<5AVsY\g[TUPORJ=NKo8\o!
t#^j:>,2tP!V;D`n;0;&<(\r@`r!Be*[U&KH!TfR89SbYEr0*@]92GI7mD;MU'X;LT-ZLXM[cIF+5Xf$4n9@`>2pJk54Nk3#Lj8qVL;G^D?]H.)TiFOc
YY#?n,N.t>GCU!4Mi^;Guc$IGCk[t02<A+2H5A<9HW@9?oFqTsW#J,bV*gGIc>WO$2WdQ3H_5q]#UG634]$G3Oh[A!@kB#p.qF0-eROe*T]'QIG.<o_t
S[VtY7c5OC^mg$]&+P4BK-"b,$4W=jrB".K,YJbCIj#<e%%t;PQ8phj2Rb$A>0DsEJf$M-;';ADZ$&YU%l#[U&Dj;FF)m[4VF7JRCNNcRA0r@ca:$DW8
RQ5e,"W`kCQXGOI3f:?&[iVR8(d0o5:6SV`'/8-?p+^qI2a-L!CHF(h?BMIQf`QW$EhduX@U.a4?'"RUEBkdMT>#5;WK*t*_$=fp&Sl88N'SDe4=ICgD
U#=nk!'2T2o?$!2"[H8'u&rl%=+Z\e4o!)tfLK+/'hbF'>L^&0lQ%!@!Y][TJh$Z*Zm11#Rb-VDR\3"j]V`;MnJ$Mh#+'>]*CAN/Lip>0s'])9n?[XbP
rZZ>\IOHks@m<n@rPHi-pjPCud;d>d!555Z"4P\Urd90$J36eH52_3uegB'2LkDHsecR[@jEZfKQ3Rfi&q1Ytf->\MfmF-MF)i=B)fqs[-oBHCNdidEm
B_UWP7"VCX8W>F1^S%TB6"gHd'(3/quM#P:'AH3(Yk.?fKCX<P1Q)!"F)(1EtIO,=g?^[d@aD0QOD*4&Hn!D35h[d/#In=dg2\%"sJ+HW-T90M7+8M2s
!*k\'dM'7E3seEG0YB8W-)Tr4ki;'+\0%,]&l88..`m!O#;qq&je`FIWh/%f:M\Yd66ibM,I$*cZp,YkG6un8.f+O;>b3:nrppmaEgWc1ENRi4>Y\O>N
$bT\N$$)[rL+"1J:Cg4^/bD8&\=J'9<,1U@!PKkU;i:1*Tf#+A\\sl8AjW,6qXNW]%<]db7s=R'%6ZR3>E4h*sj<NQ,`_>'XgODGlU0tqS\[%DI_9$V%
&SB0iLM6NoPdfk'35fR=FD!XaJUqD;PacYjUi'-%Oo1L$!lTlMmce!+G.Z[`e,)md=HuScEZ@XbV4uqp.i&n">C\KS]+PX?Q]qQOGS0<-7__\]3Z?D'5
m('Wg%=oaC'78#ot-`.<KAD/_;<les1C$2@qc7M]ba\GXR/;GtH4"-c216s"$%<18sM#4=QdN!"/RCPZ`eL)ai9o`AunrU0eb-(.%c_(l5\'PoITk"fQ
lr"ck0&9fb437Ke?L#/3f6GP\1\@HID,ZkI:@;f7_Qk)8)1Hb"8##2##7kOK3L]9AVlGVE5k1_=;=nGX-#aa362C1!Nmb.FTJ7<6B/Q-]2OUQQs">LZ-
(bU>X\)D-[$`_1SU%Q/iAjbL:4T@^5C@X\Dnl6Z/n@/4+dorYX!jLBQO7"O3M.$\MMH0&#Zq/(X2SUV-s.dbWB8ku$-gBV1P0_sSV@:ZXJ*^1or'.Xb>
uE\j!RlO;&k6os/M>cFlHH0+bO%\qO:\;8$H!op#NbB2hI2M%]c2XWnuTH\,`Z7]rLjcp`/p.XWA\]@33HI4Ma<(tc3u+r(q90N(eOb9--Jt,+s7NU#H
Hm1Q_SRSV`Ij>K\>*=Jr\G#YB#crOk`$6SKu.pQb(?EZb^(?Pt*mnlDX:WCKhDE5W5s"b(L"\LIrM!s!sShKBLr&,f#5m?%7e41@0Gf,@&,>h>4aT_8A
h%f&X9H@]DYfEKF$)(jBdqq3IF&pN`d=q^Kbjgr5.*`>YCC*=jJ6!Me"K^kEsXJ'GdL#Gb8`jWa:]O'Wle"\taM%-0Tgj+ArO-9.3t;*ZbgWUP81'7-d
\G`0FuAgdR[F6)&fe/[,u5AN2;5]Ra^-pts4<3f%Bs%b;RfE/tkX95bAaX)qHao2fQA#ZgDFjojlF*<Y"bDHR)r2ADlU\D/S:mnPR#@$-1i^S;Wld0>q
2(r_mlTq8T[%F[Li+PNUQRQp%ELO3K=(p[F;q41K+GooUTM$in^\c-iJ\h-Ef0+gQrZ!^nFr\bA)tP4GkLthhbO;IiTHY4fGcO"I1>7d@aK<Q:g03RLk
Q5Wh;<-MFZQJITPn`^/\pgUl>FWJDStn2e[GT/^217-3'o]1eM&G-;8kK[J1i(O)9a__sEFB(jFSqY#U42aM@;lp).T-4IKUlAtfG"tkr/;YB^Md'a\b
1^0gM2E2'p"@`4mjsqW83M=&tqi#hnN65FYh_;`ZJ;k4G]rt2$C!RZf?="V`G\9o\g`">panR>$u]bJ@iWNmmWbPL0Bt$Z?))i)44<!"hR(Sr(?V\i^S
TKn3;*Di)nfU6Z0q<CD*."=HIW\3XS:?UP1d@-a/W1Bde;9k,Le?><;b'?Qf$eiW]-I-2$P5dl]lko-N/'!OqiYI)'PL*qg_fG)-T.+@OgNV*3J02tfS
Y!qqUG`?aWdH@!51lWkNtH#5QFI0TK?OR@0<T*p4c5CF"rZQ(NcO:A!'C.9u=ffmjK7QGH&T\B:Y<L_KFdkJHeF99,=qB=DZk!52X6SVQW;(H$P<nqeP
?amr?&2TA)m^XS=fo'3S0=O7,"*uT8FIsQq*rp_+MTBmb4)/hR@U:Ya;pY&s7DIB(Xk1EtDJe-g[ol3mW-U^u7k!6]CF<n&d@&ZO^sP@g^7@Rk>i6/I`
EE7!%Jm5=fRDL&IZ70C?oGp;-#GY],/i4h,[EV&`ZC+VR%OsIZ<rD#8p&,?ZiDc)3.ME<d"eJkJ2SgRF\NV%?H(iQO'-#,5\@[os(-,/h6(mL.:>CXcs
3W>XcFkCD+G#t]Bra#&.9`XeVD>Z0)<!45VLMR-S%?fINP+%e^Sfbe1_mU/FEOdA85%Ja03jPi]EJZ(.NOf:/`KoA\hgtAXA#5+G%%bk:ni0J'cH"JFS
*lEF;8>djh\[D3G``]/+=oU9Gsmf&R`na6e%>Q/oZ_c`kP\1G*/&E.@b]P.CL;3H:/2>[bj_K/)ZWN]^.=*e27)b.`D(-$E!kImtX>+5AgnIjpcBQ:+b
q2QY!D!i,RQAUq[S$7UrRn'C/o5HRAU%m,P\l'Jq:K`,leUd=:WgH9pMg,p1!KA]MC%r*\:g+I`hodB$4f7a`J":omCi4'T=><"pr%2gujne=<(L2S<<
6K(OKm)('o9`])]Ama"=b;5:FRY7-Kco65[*km<j=0)a3:d:"^f1)#k-8qAn"@9PpJa$e$G(1E+cF.]spS^Y>.LRTYYo//i\NYqQ_qu[I[k$S%,:D@<8
?Y_1mgTDj)aAM9p<S)R=+_=Ti=p=[VE5.4ODIH!8A?UD%&qF'X5*qLpY%X3eifDr]Yq41='M!N3t\f"&D$V`d/2F_AWA<q_3")plIP-^H)[W/1JbCB*S
1[ihdL&)J/Q?_=X\QjLPTD<eJ%!\S\DT28hKrT.+:teOkA6h>$>EA6I9G=fG0C2\!(/:/p4@^.?$5g1p-XRF<F5[6+/dYFC-D\Heif(s!H@f]1[Oj"K9
5VXdfQsoS$Fd>1L++.Z-p'>-^jsDg$+U!)*ReA8)nGL'qQnH&5"3ZA8WYct'FF?V0'FZM8]eg[p@:oPsKsDn[@O0aRjNmeT,e]7uE=LZGu3^UC5F"%fc
@iSN(l<4iTe%Wpl?G*#g+bq_AGiV@>ST)PF!o,uN$HAK"ij6_IE]3E';#&6b*5qD=O(7hhsiVIaqF'(5b^Au^?@B++5)O^:QZ:+U.YZSId\(SLK@Bs"`
BL$i#*&N07N)fn)=,+MfXO,YJ?]AjAb]4G1&uVBf*cs6@,ouJj:pgmD^Qa25AFEeu2ICP2TT1F=3i"I[ISN>#i.O$2PX,##jue"ET/W/j),:ms*"r=TN
p30F?,'>/!?U^]-O`\8P?6EKlDjj!J>S&aJI0lM.HHC+DM`99P(Fl(5BRF91_5T$3ph@c]ou"]o\l'3TM6jVdPb=jf&<%6?emt5%Qodl"e-[g4W?Q#p=
JZ3c"ab5]u'/uPZMH!BB^_r3U79^<1;]m;`<)]e0It-WKam`eZo3n+?o;*geFpkiQ6[]P.)@f\$85tiQ;l0Uc84!N+,fT.#?OjTMnXUM;]h@,C6k%SO[
'-=t]oVRGm\RDMi-S,m`cXTQ]:`e]`*"J`aeD!Fg<)S)h@s/C4c;PQho?6A9orQk+m8lQ.F&5DF>\R==,BM\L/0't90,9\M_@H53]pf/3>)3Wf3K@[#)
s5K6q;`NDo.!1GUX%sB=Qr<Q>U(mn!2gWQYXUT&[B;sc(Le`\,@R*a65fl(3&7CIi8<.N.&+sBURL2Q[sPbUCi/XiWToMI'K3i7?5arJj.jB54aZ@QeU
8gK>6`':!H2^M8Po_?gONQhMoMc:T*\4VUF1TNLR@lR(\KBJq%>!Wb4#L4u2*e@+fl<)F?;:#5)+\tbVO7WK83\A#/CZQH"5U(!@=29>M93cpVoC],.X
HJ;VC)1HjYl>6@k:ln>f#5DhX_?`*cRPuGQXaI.,Z%$qQ,>5m*)\?25k=LrgUcX_^V_0pJ_)D%)dV'`qS`.>X^i<Bj&gto(N$?5jPGSA>i.^GIeP.LJ8
P!o&XmnY,sq;F"2a>)<lU9`'p;N(dK:QpE57C-*)/Pl0lg'fCKQ.j54/Kp-dqfk$'9@$rXU"t(,XdqAJOiPVe*KhA5im%7&Z9'mc*S$K(C<5l,$cV2^G
S[.MpHs>'&i;)t^W1]"V._h5LCN=o[Xpn:LmU)_nNFo0D7C>M!N<o9_.%pHm`O7t]lIL/:cWo&O_XrnJ>VG5](d=If$S2q-)M#J6il5e)+_L\,mf!42I
BmG1953;on\*FEDlWkcgT8jfBYi!drQ=eujFBSj:I2F5^Fr?l)<.`p9..A[pBLkhNfES(278b7luAM*>s?i'1NgGF)jh'?=,SBer5R8du^fARV"gu&AJ
Og>)9Hp5L(QT;Y1fNpAG8?g=0%\+rj0KeY?05!&-F`RkOj*=nj0M%n,moQc?5Mk-`d+29%>119&XhUCg,9.oHhc:a[;T,DHM@OHI0ZU9A\T[I4r%_li5
LIOHQ2i%JqG\r@RbnEAZqcooVP]k:p?6tq?/"ZT(d+Nhs16>FgrDsW^D>f!$]u0D'4LAsL(k'QabOOEUB.4M>5r>7GhNtmiA*=ZEk]>d`*3>sC]kId>#
]kX<ko_X"Q85t-SR*"X?0]>%)SRU-\;40Y>I'6BG"b_fMEl-iW<D>*Gdb`GkjRn?=qd\0IQ-c&Z@V6q:ihcO=+G_@1a!-aJ$QRZs=u;9Ri)URNKbVRA+
:#()Be0QCo:7/^R@%!,$G##.(*MB]MJZdK-UuR,$Q+IRfc?57k^==1,0b2Md[F75(l"4mYNlJDW.F9/)8W[ZiJ"9r3e&`[I%tUsa$'O7GJ)9OPQ#WfOs
3)oY(Fl)[Qjh^LGB[TJa&QIQ,+/Nut5FtkN2KR_7e*0,?ZJ\:n23T3Ro,)u5*p3`Dfe'LGTglm[mR?hYkJX7NC"5^6WlU^q,);eWCfORB?%SVhin>AL%
3,Ci0Gjh:Wg!`&#Oh;=t=DI"FE'o6%jj(Hsjupb3#B;;/7TrOV):!_Sc/"tqKYtV8mor<]jciCLr]oUV-.ern`C^A:"hBQ0Z$61/%8DKXfpB%(b`?$`<
Si0Jr1;=*qPKp2#*TX."Cn@k'lsRu:4"4FbLP0&.o7Sf/t!('aeD"nW$6YfXRI@r`FAW\_K%t:=m&r/gGI#Hn!m?*>Jn",2l"\K.$_u^%cU=qS?c*2k"
HVEV7k^KiM<4%;Xuf'GZ\6_KiJj<[YM_+_)/I)aKm?3_"Cq]$9;%A2K&iJ%4`d$25Ng:?E:pk(Uoa]A%>JaD`mds,JuYI2_&:oYHtg>KH.ep<j7#VC7'
t:`bB+q</1]ej*_<q!42P]Z)Go&5f4*j(?=Or0nVs?95tBu^S4f?#^U&K2;pl:*I;oZ;F-r1GD=B]Z(T=Ik)Pm`hMg%-])g4]V'\@h9T&!t`?l3</*H:
'9*<^3AHHcklp&CP\])_^0]+/mA@r38p*Q;#UuR=/379#L?jDiQ\EQmtTjM=7km@Y@4?Z<MVlcCrP]_Kh2aYep<5m2%50Ns]b;9?4pHm9N4+-noo8hVh
)!qLS)_HbHrIutdO]ZQ,5c_7IE=F15\gOqZ*L;ZG-$HkKjj?Ue2tgUrpOkY16>Y3;Y^7M$"J.-s=CWPTdK5=kqY?6Ik;(cYh<::&"aGb+:.m_+M$6(Lk
Q!A?i;0nC<4"W`^^>A;"5um?/'p60Dr]TW#QP:/n_1sS0rlu90Daiq/K"O15FKh.cjtO$6<AV<6\nT**!DEL-tjALgd!WRS/[S0fk<<Nr-uG;'-V+9-Q
A]=5R"`C2VH1)TTtt!7&0CB%Wr-Kq&W/.Ju*>qG4#p%XRr5RHn5iP?A.=6"$ZR6Y#0V\Bg-eY5ii"@bX&ka[:\`/-uaR^ZGJ/s6\e6f>H`0bn/?,l8>Z
jMMh<E!?r?8f1il2L0qiF9akuqXM!aZ_V;e;2q^!OIWtGURr)*js&K*+TKs&?)S_6KjkMV9LN/=A@EOk>>Y_6]J^mjH+KIgED(O.\BZqe@W_T9^M,M*Y
8mbsQ06#3(G<r6co`D3XN27S<JQRWo,DESl:LI_"S0lnU,2mk0n=-!"LU'CJZ$FZ'IX"04%kD3]?@ZNa;PqmL5<=Sj6M#:B6%E=Wt";4p"P3)$fPL%0Q
i#n@%os<!a4]Z+WU78:6"_l^TRclLK\oqt>.8udM*N\:uI[OPr[YYiH&0\d%TdP?AKD`;>Xg$Fkg^RrFao>\^.T#90#;dC4R:2RDki>bs"T=7I$W'>S7
S-P38Y?Fqgi$P1j=_a#XS(*RnkIT3k2=V18:2s!A*r6Uk1WAA*KgV_@A(Q,\e!9fDSnNfd.jHT9:F_5>,OF65(N"Mq=)!!4o3$+rec`HB/Hi3e0df7:V
+$)/,NtYEgI9?^8;G'MPN&iJ#^qeF/Af%icmqn)M3_T'KRV8$[oN#QeHAuZq@&V(N"q/&hhK-)<cuIdQBW2XGGi:GoKBUpcUc#CGEB:r[sg<L[,BVp/O
'.F^D_Af$"\08`i=<[?7Le6U#^*ar-^fA\i:EDu.!t@DT9M[u;agFUG*<Asb;HhS`r+//aP&==7lE+rEm4ka3op/qrO1[)C'<<e5=!8tk^u<03ZfIq1/
GR%N[YX8npFpe@SCmR7D^!MZ36bX0I6[d^f-HtMLkJ`7M-MK6k>]>S#uYspH`[Er.q[ZB-@mIW3J(#U5_&bMC@H!GI*?&(r1Ei:o:p'GXHKl3,uqR7PR
0'nOmJZ4Kr=`BU/&'@OHSiXM-;%0^)c"d?;Wh5IgLBic6O&SBtjK#fk+>cl63J@oP)s=[<=K9N3ph<q31N2>a^>h$p4n)JtK"AT]Y57*"YO%q:6=7k5g
>eD]IW<&qRDk#QQ51A(]&KMN4#:`cVLUNA@%^runFMG+YPZ*T(J4U9N+#VqKNQ-:MpU$.Qql1G?`9cJ%@E$@^WIhQ[V3RW+Ku^_Qn-rL,VA=NX1g\FNW
7,0c-M/kKpPI'`/^&))'S)YI75FVWX[A14.PkjgP"+,C0)=sHRk?]BE<?^`XSWKMJC0]QPPs[]cPRef&jNTK5O?e.u<`^a>NS,<SZEu(l,R)AID&Dh`T
Z?o'8lCHkV*_Y\,fMF"''Y6#DIhkjWf-3iV(uoupUZPR3c>[O;6#SNm7kiZOlV8&s4"cWg]*74?n]ZpGM@,i##Pdo<RaFaaP&WBCnJG)=oQc<)p+O^Op
>T!">O"T-XY3Qm/="td^=jl/r0na8gWJ&;:%bl17=0g.IYm6ktTHH#p0B#o,CC%E.i4//C#b)7G9\PuWY6H<%VTqhR)hWY$_9\Aq4JdB$?iE2PBBSR'%
e:$N-V`#f_WlcN]75>uqDtn]oKnfbW*I6]O<sYj5]2MM'5J*ZlRK./Sj-]uC!H-ZbUiGm">=M,>oeT;g`-?k0:nJlj)ud1=\bg>=5c7LEG"tcoekWbI:
dVVM[#jYM8_B5^Gq_`2%Zls#Qc3-Ul-1IZnBg]JUsjUpr<#]7nZA`?!]'?EiDJE`r9QW\L^:U^eu4T/[#\Eb34.-_2\G;S1!Bu4R#EoAEuad9Lt%0s>H
Jmj2f5otY$LT;e"j*bKt5+[2Y]Cl"Y$)"[LQ&19'XN>#R`1pU+H8AcLAV>A$d[pSJ#Ij9$jElW>SpTh?9".0?uAl7fs]<K-XY8PSu)84o"LO>T5)=#R,
ofddN]qo>s-M*ia%[NtYJW`3N?q\NYS89*7&.A@E=In.#BqCeaV$=2_Whe-+B*ncLds`ltF]an,rH1i"FY76VILEPL)Kq+t`%=QNLA]CQl,?)_!7Fi!_
C?SGi@ndnr20E@cGd<M*K2Ndn'@WRC#a6scq+:QSKK$JA[ES/ju(*EAb@6PN2\_2os,:hQlrp1W'j?h]p33gcuJee4#KO.86-?C!ol25:no(%CgY=SD1
IZMted+ZkBNKZQK86Zb:@BDG$;A*0!C?4Z1U1#Ijq9KW5=Vp5/$f6bpWP/3;`hP@GCt()p7Q]@eomd&S9hr#4GgJ+_>*a@+SMr1V,BgASQ[<H<s$KPfm
O0mOihO0e3T2Kr)I[0j.<m7[.[;**WiY9sffR+Q[D)Zl2`U7$jND^SK"="CJ4fPCg[B)s3HP>BT36%B9'gEha$!,BRNGQ0eCH`>IKmEU<hF;iOBgk#<%
Z'7I3)m<U!dqD8++.^BS5g)&`]87WdJ.VLGioV<EfcB2,g(ThYHFQ4(MT1T7$N+J>tloO**Sn.lR2nLHJXIUl5uc1`RK$MRamp%<fbNnI+O<dE,d+:f"
Qil1JB5(_:a*>%"[Os0?DXgTLfjd3T/![kc@MT:1X\;qc>t?uUems&Q$;nE6^CUX30;6sNkGFEUnC1?`;GqZBbhmLAg"<*aVZq#72gjMcd/,?:2kNnd6
?51<NH)VY%0aV()L/QQULh3]Pm30<mQ6&@]&V'p<%+-E^JC>>XQYNj3r*ELojg8Xs0^]C1Ud$q;B_Rh.q4=1S[>HH3,r[1^ZF?7]!Bg\aDCor,besg&=
>k[+17IU3+SS+Rk1J)#Eq!*_@_U@5/Z!cd2K57B#ai+?SK[LL63cB;]2lAHYbH>?#k`K[Nd][V2'sDoN#i_Og#;H<^`R8`Nqh8OBA>Wu2?e]3Jg<Nego
cO5(B&8St.?"RK8m2"1s/q?;1]WnC&[]19oJsVND7u:Srm`q6Pe=u_e79E:0g/gk@t%al@obEHq#hY;cq%$;f>%t)!^a`!2M/iTVi*:$c$q:/7@c!OKT
VDuDZmFI7&U'NeA9o/a;<P;PnK16jc2OuKQqL)d/ZR1;Ie<dLb'O5:.RWs#9[WBBP`X)>]!fVq*>.XO\Oh,@lff4,9dAAh#$J]M6#`I0l>+nmr`Vm'XT
E!c>p3)n#u&_b+M;QQ*_u-\doAaGfF2irK>W&RE?,m'1\X6OSaNG+Vm;7$=9uU6$1l^Ia4\<k"gn4NJNUGb0M_<#Z,lrGsoT&c3"q<`sp,eR&JOEM^aU
hC(;!(oeklWZe!HWd0kot+2bYUWFU[Qhu)UM8h062+JJs,-\E`6AtSQs="]JZF:1Zo$!/hD[)2b?p4R?D*I=:][g9!kHH"nD]^gc[dP;LnO'r3c9J^o6
h),<D^TC^#^II]56Ai?qCoDCT$:2K%#THE)IS)a_cC+?C81^=;U9Ze"G^0nIc"t80kk_c&89Jj>#2f?_@,Y&U;!^elc#9<lmO*`b`ab"*>..%5r1mW\-
O/XFP)",9O9UY(^d+1L@UklT3nXt'O?<=dRZ/?1dQF>bPbIbuW_\B8(D1--Rs$=?46UgUVTu0'CP`6&'Rc(lcS;1IW<dUqPXL+cnd[*97oK^BH_1USdD
5&i2-epHG^#TG,I:lq<f+SuelOOW>6!:?3BKnBY+g;^&*^!K)3V2/;\fpEc(`9RjZeT%O"I<Xo9f9/0aK?Zq".BTYStUIc'JX6MAPZ2>bGn$cWZW62A(
Kg<m];r3XH#RR-ludjA2&`LP!UYFCS9KJPm<rnc4jN<n=IMds7`e1(gT23\,[Vp53&P&=$A`S16<q!On88s6F00StV,i4YNsd6am?;)Ceu9"Ijjqk2l?
i^M<3M$V7S)b6hST(h1Th.$%O+dAMbI3tPD#Zl0s&?6aO);#*nI:"V#Oi/aQPn7gO*5q_INh+rPA+f@JM,SC%:SJnW$'>lBtM/%UFO$DEWG?Hi\UQXKX
WV\L1k-7/'*.XF+DLqSWdhYt.AO<:9*1[Uo\lQhUc?706-Aoa.1d7"[>\Yf>%$X;q*oLl<=D)q:"#/!%3IKKJ41$bUa5tQfA)gh1&=<7NEP^csY43C?l
:/jX6Hq-oqZZG9]3*.j4q]Q80S^_bLs*S3D<V[o:9K*t#2$b*bTrma`7^Z)me.@l4@7L+K+2#9lbfRMrILP>r1&70@:o:(2&9W\McS^KIa#J*9F9bo8r
N1O@Xh[rF<YYt&Y01>,F,8*dd.$\+'6eu9b-c/h8(O>C8+M^^%;X%W^Xi(bUB!=MHpiMVfr_&\WoE#B[kHiV]!5[%Y`$;;85NMrJ/*r2Ua<mh@hJQH4N
M"DRU2u1FAKn?);,+;OMjcRJ`FLDMLRn?K50Q-7h\^![Y$3C(b<N>$1d%%Pc9P>f2ur2B@8MZo]WL?1.kNlg5L?m$FYI3a,$hXJq.3%E.#L'V$&/eBE]
8$k9%[9uh6QV[DES'O5-[:u&nXqOh\U[9nBJ-L3O#&\pk6A<e(MLZpNP\3?bXi\@!Y9Hlm1#Kto.<UABL1&'ei%<)*Y'-)K!g2>V-g)uYU/BT8?J86FK
gkCd1p@CKdb]\#s-M2Q>W[=_']J<T()3oRB%n+8RC#JFm)4b\_M^dA[J,(pZ9tOp-IDW00eP#_YUrL"3,$W/ls26ZIq'NXW&,BLtG;cG:3%>HSX?dme$
+"`M4:M9gN6]M#A34mVKH=i3+re`"Fk'[1a4t(lJ#%,!UfCLtr-jo3nGZY)a3d:m$$<ihmD1D2kJ:Tbffn2on:%]f-0=h[$')B1*Tm*H`&qDnb#>2Z&\
t\?e`Ec.\#S7KXTO#&m&&eO$ZmOe4qNa2Sd9LY3n3.iB;VX/ZB-3c=I\2i)t*RhL3Nl6T[PKEk"2MOZR*MrC'-'^ra-VF(0,F.@s6`I>H`_CdEK5acb>
n[R2.dm4#0iJ=cLH+dfhjb.TPCOE"jid'8&+Rs03%s_KGo\a#;g[`Qa>ZHY/U<-+fN3dMJO.[OckZ/l1\6r@ArFT;:2j7?;;tojO#K2sg&(H0j_]I<6b
>HJPT--6$'6,odZDACa998=XBK3l5qhQnl-acDZ=b2lr-MhgH,MfG9:F$q`%U:-.un*F6o,W5c![gXRCme54r(r%Oj.+2f6?`!*M%&Rc+&8agTVo)dAt
5'HH\UBFi%i<TlB/YL`01B!"04t:jY.MR4fR,OL#.L\&U4B934k;T*K=C743O4h39HlHqF`?7T<&]JY[Vu8n-qEpu:X1+>/+b$^=!qd;\'BdlW7cD1O6
CVhWR;87ZO`Um$$thPZ>ZchY6h,2rh1_?^<YAo5!pYi"m2Dlm&Eig9ed0u)_FZe2C>R[HV!DZL6foMsnBo,51SCt+d"hDT&/u(I"^"Aa!IeF:a6)J]%K
r*pW=<Pu.u:[-q_jmA#@#TB-\]M3_FUI6=FKFA3m(@b&^,_+c9-i!QN;g8;U;Dt/2=!QZ+si8+GIaj/5d)PJ#<HZ/K%i;q/?@M[>"G;oE.(F@!uSnbLF
D4bl<[:f6`=n#2Br\Kq"BE@6>aQlGJpkU']n8!DDQ&dme92,6JYG'W!O7#!K^]7]am'HEVnNc\?Eo2(LQ,%^1[=ZKKs+BR:>!=Ytc;f/eoZ9Yuc>G^V"
(eVK(=ZBKhr]ZleopS>4;\:BEm'#t#Z]YOr`9,i.Tj)_4@/[&NQUk7h0!=^1h=ILq6,3$e&P1ScP`W6a"h[+C9AoRQ*A+@:[3*c.%g9,U)0l^:VG:h?a
dV+$eepD:)W%<BR>[guLTY`W\Zn_Q5^)2,g"VjCSGE]%9A$sBG*^6RoJPf:po+jej<7=U<<*fVGPPrgfs%m-u9=c90YV'3FrWNWXFDDcsA=P+)C5R9XV
PA5"gIcp7"j"i"K9bfHJ^=rIE&iNM]1MU/[jj=ZX6.S8PIYrJ)FWN[88-I6B+AWlrV$o.4O^3lXjQ<>`+-ngqQ)`:78a6[rL0FWT9_KPK]m6/?8X<kog
"N8qIAlj(`Z:(^PKT]g+R(>eTE]9Juc<TI#0LQMs)<O:O?rK0h;je<cn]:,(7EeE!ruSS)@hjWi2^I4d">N7Bi:q^rk'lD:MIB.&fTuCW&Y4KZ+XrL/m
Q&@1T#!7h:f@QH;#V[B<7$b^!dZ*n"9$VYGhj5bq#'lNl'S9.f&Z_k&IJJ($.r:k:Q3Rg$n7HEkj+`L6*VVQSG+"aaA@SakWqTIiQ1R=u%:!8'_7qpC,
U^@?gi-N>_NDb>^FL!edpG0e?0Bd1:38@)[TiK4%tk+NZ:HLTn=R(%P2@\ZqWK`Bsq0`WN[kdIb&rqaZoO:L[PP<:N.QYn;j%dG$r3uZs+"CF^iL9-MY
a=?XM'tV[7/'+r@FMR$G.Tfr6Z#r@c3MZ[fFCW#V5OC*f2jFm;^""&GCT8A%l8J`.B]u2)FKLf@V?fN_I5KdfCs(F<KPC`iE6%gDa^2A2q^Q=!%3;aD!
C^De24q%"q-5JN(:*N/31gp&GFp%NEH"2!C.\>>M>/:%P1c\j12p=r6W>]$W,oK^XtUoJ^&V'X"9AlgO(!.LhV.JDil;n$f6eKp[2:+mg#V9,eTrU,fV
Vi(NKPD%m=Q-^U;V$RS&p>i>;`/@#Z)UQaK[jg#-6iZ6q`i<!],<#ql3.4MGO(Yrft5:E1lDiBH^T\\k:>:*(R[p#!>UA&ljMX=&6\BXkFT^di5,ec]a
PK'@^=4&hSY&SkU!]Ue5\M,5E@rD(q"iEf6Qd_0Aa6QHb-M#`%3O%8sRmK8Ckl66N["m530l3ka181(.e^IgO#.&h@/A.nXMj\^7Rc*L(S;`%1o.BBpH
5nW94q=1]Nlbj'M^CBp4W5L&"*`<''**T)L5Si?-n?cO82!l16'<'6,.$S?serQDYc9:+*WaJ&E4%M5,E7s-tSN2[ufcth3e#T1?N9Hrr(Ljt@O0nku2
p9>Qfrm@Htm.W=_5Z7q.AG*mTZR0S<7L<i^RC'4T1SB+0Y!iSF>16W^:<36s+)rOMn!hbEK^n4D=`4f(^sbJ`@RD5;.+#CD88Jb)Z++lZjB5Z#/&;9r^
H2,hV[l9@d$.j<-.3P`\H2l2hY@AAUXse:D@N')V##9[-a.c!oouW&C_40YM_;16>=>uk$/,,#@1D*l99eLgfW+$Q3Zp\3+48jf'4i[pCFu(2V82Nd7:
YKagFPd<743>a-4#hr\]0-Q%eVJ_4jB#!W=2F?W36g)eN[RO/^q:On!FlNEmtWs!m@2u9uM3%5R9$,pTajhQ^ZbZj`'c@BM$=#4m77E)Jk]pdZ/c;+!S
JMRn8@$>0%=@J#<D7KNKgiWK4>3VVk?2el'"D1ME!kd?.4PS^;?dAhph>ge(l_P@9aP%J.Cl!u79d4ZZ@>761c@\Vf>L;Eg_)^4SC$6_WZZO28&TG%Ll
dBCO%]WnJU!+e5H#7"rlu;'854<@8][OG7n`6%O<<^#a3Vl#(DA11qL+QX!5/1kO6:,8P^O`*]`8#s95Ee%$tM!Pn$Ibd9S/YZ9H5gS(KLUoV'2=qpX<
bB92YEE`A<77mt?!D6B1I&II;deea3q:]V0FARG`e'.V`XE@`AqH+0B,@*WA=/lel8=SbK!1YO@V^WC(P9+%i'A_b(:1]p]\80X:\WuBghhF7.cPY>+n
4]o2X\!'n_E7MOR]SmnqnsOpp\cm,VbW#hCF/I.4V8'c?\9B)ckgqG7$%_[VYW!0=;EV,DSGj(VsGpQZP$'")[F86Q*r6o0<C6=4dcF4Za*kQ$hdlKXq
6olXt%P#r&i5tTURmhND.eWi)^-,YJ(!YC_Jm*e&R!WT\geW1"CT"H3i[A%dt&&0Eg)n/'4Ge+'#3&4aFA@2B$p/^gGH"`r^M/Xra9*3GUoP1HB#Y1L/
"')TIMhccU>QUbrC93M5c]gtRVD^lL3Tm4huKOWfH%Nd_pp;mTp#?I4K94F@;t5k.9;d#Qp5>pCd%,(=8&:S"uA;sh6=3]CQAqMo,SMnFn/lc[_u>c7l
U+m+]q&-#q.p&*Z9kAOY9'=?dEi5b_GBgiI"e7"jK/R.3K2SERZI-Dt,FXZ,+?&ak!cna0-8i,r>.p5927.kii$-9^;B1D\%^-`U#Y&1XLa*r1"qEM6'
*&c)BAJ=43mVAH?3aT`?3okoNP/RdlTM%q<O,M6j=':"hkPjL!6?rX3W)&+DA8h#=6ui`19m+McU)BW>E:TC"19XIJnoFK9]rj9L]=L7,"YuL.T*%$p+
@3%G.`GloE.^u9?8j$ceXhIK-%2#-^MOBTZSZd9.*9mLm0g_EmbBCbChGd%,PkE_O)K2>:=oX>[7nG3o/I@5;H-b"r`'PUk[FabM3I9Af#E0"V^NTdop
Mhkg3P/tjjjS[4IRG`j*JRja"_99c]8TPZ>k=Z`(E;nU+FMrB-Jpp:WDj$^#+nD"i`=[m*>,SDI1H!:4!CF<?<[Ah!?GrI]h7IZhrE*ieR$H]\0h`K"c
?=Z:,P/h'da6T#LlFT0L[;QYbXt9@CF7"t+38j<$EUJQ))[j!8M3Sio[bc+Np\r#tn`-oJVm+6'.1T!qAknel=ADo!hPnFO9,k0G+TXTCB>PA&X(f5oZ
!"%VC(UdXg7BPZa'r2a]j4Y%cV<T#N=/C]f[8!P)2;6F9+?h<ATogNmLR/PnZ;e'qL@OB`NM=bT#Y@p`%+mH`O2>BAGP7uXnQSd-c)kI?F?l,j5oYM#!
,dIFZf`bu!<t<+FZaAH_TtIam[7Lm$,^;r\>g:26G2@hIM^ZjA)b28F7GkI>n-b/dAisU4U0"q/XqKp?^,FU.ZNTMKnM-T&E4j"Egu1.?P>JH\,N*ZTA
b\?_C_:dF&RBfT4JZ![EHi9E>t)-9W]>Oq4%TrNc*R_5U^pW/$CQCQ=,sK3NWGt;k.>+RRAe,KYBG6>EN&<0n]/iur"@Z@H\)al*#e])[pXlWW`!?0aT
"oq/&5%%$#),fnPt6c$fgR)/r*FjDU&h(?#fO]05<:B-WI6rEo^OekRBPA#5eddD]m@$DKUQ'>DV-A>FuX[]1.i29dgGHM\j&&aE4[+]"4.sflC0XR:*
(HiF_FB9*o(0bA.S#'t<-/_A7^(hrq:9F7_dqkhE[`E%6ot(F:QH,"Wps.V6K4K&+S%^i$FC;EM*75d[3bI?b[e*6(qcOO5\I1ep)2nQd<TnFKdt&n^#
C0(gAT\6tD7E]PZ\a3C`DDf.l&\4<4'7J^(6_c&bOh@+-lRL3]cFJ=so#k^[6^@6FF],C4!^C99$k2Lit`#gK3Xf[d.^ToO=Z,cXLUcIFc,cG7gPL%ni
UeaW&:fh$^c>PhW)[Oln"WEj]8i+=FAPSPpg#b>J.hruNRu^KPI=BD=jZ!5If2[=p4X"=B^i?k-g<O01,^h#U%oMk&D,DdX&/EeCNM#5R;])#6O&I/ni
W/bX(Z/<@r16h$T[%N'%_A]d6IVO[B]^&#U4XCFM"3D&%&C*a?+0>+Og982h@u@8SZkATbuRB`9CJ)i`2$'QXo>*_6!s![NT%9b#']9+gpS[8qaJ9OCt
i8qJ80D7i3HQ>"mssaF.7-'HSC0!A5a"kY^,TlNb@>*'$[8oV_iGT]b!h'%,_se:qcDBRM"$0Has]T7m$f15IhXS"jjW[kar0^=K7&DRjue/Uh>dUMok
l*Y(h,.SfEk(AAW.-i#LksiV-Yq*eeIcq:`lb/C<kb#=83XKnUp9i8s?=c#3r]eV((mYhO2))?"J7,h\p/K_lqV9RY8l"80UDE*Hn[F[Rt&(OD1s_gL"
KO;`&Rj8BR[_TP_$GcTN+ggSn]hnb`i2e6tNpl_\:J:l4'Gs*LH3b`8k19BAOa+&BlL_/poO%H_Cbm,]*qKUD';LsB)b7i@LDaqlXH-MMAJ'gViAQ7R"
;:r=.-[*gJ1)&:oYn9dl':ja"UQ;:T6]hV8p7UJQNaV*6GKC=j.l,V6G2@HTEf5]a:UYt3b9AT4eWF;6rN'nQ$pDmjl%4SY#Jcl?QfF^qE`=`8MZ:OCL
-@kT5/W&@MQE/]_u#i,JY2O9c]7-\*"$GHi'pr#*/^HE1.RQq*'67oPU%u1fW.f77iCmJ,r^+1mj\"/6#m8SUKuq\"9/_5^DOgtW^1,!kl+[o3aK*lg,
;/)1:BR#5+d?he^9q'"ko/gM]iUamj7eAoc[k.8;'HKrqpFb+QlJ9f/8\VV"AnmRdcSO$pVI@/ZX>2C90ZjX=cDVRTU$<IhGYq:KP<!'V#N*nqU5Y5s<
CLljLKdn/G[02Y;;Zfb)uFOuhq=\qc$sEDpFlB-pB>e!O$27\5n9&2K)J(]Q2$L'Xa9E%ul"VMoUO?M8UcUtV*ZciI41J!C/5=+\@i&MipidHI&R`WN4
6,EDg)R;^Qe&2cNV!!2,2!U8&8s)4"iZ,C;P!WW3#!!HG.'''
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.56'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-10-23'

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

def is_partition(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return False
	return os.path.exists(os.path.join(sysfs_block_path, "partition"))

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
		# multiCMD's quiet=True hides its own "Command path not found" line.
		if lsblk_result.returncode == 127:
			print("lsblk not found (it comes with util-linux): FSTYPE, UUID, MODEL and SERIAL come from sysfs and /dev/disk instead and may be incomplete.", file=sys.stderr)
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