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
import _thread
import time
import traceback
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 67):
		raise ImportError('multiCMD too old')
except Exception:
	import sys,types,base64,zlib   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
GhUA(CNnN&G+Z`\!NRRU?j/?\e'5<tOB/XI7#`dtP+;32@W<N0-t*Pd#QW"F=oJ*Of*hj+ALDnre*KO,B("HbF5M%OOM?/4or>"+^<)89<H7J,O6p4UH
o&p2<EZe+gtpR2R0Q<3>:"EeJtuBW=W=/JSu]6Cb+c/5a2q$oW4FV(+G9^'Wc$!8Dh;QKh?@I(e1,,G!XHtUXrcNiWm1+-a_m">IbFocg,^a%K4]7)eR
bbL->4HiJB>Te2I!2SXcl`?,jE@sU+Vd-<Pb'R&Xoah=i5ofHW<!i<9-fohu;:L`N_8<E?n>Tf4XR/SQs-(LKDNYqeH/][kB+mQ]o0Si-JB;0V:%lM&O
oj5-uuK,&?VrgiV2lT;u=#$Gl`'m,U!PGPKebVo-t*,?Vca:S&;ZniQ<0i#dT$nB9N'G"okmAl/^0PPnl2&H-Qfq"j16X8([A<3("B/upO)SpPlKoqqb
<I6F(eq=)u>aMYLM0\Q>I&T_nRcYg(tforn@8[Btn<=:Qr"?8S*q@KdX0QVbS?5B>c<]I*]/QE6hp'aFjBb\<H4hc;lG^b#S^HR!kFulG>qkrmh>f/dT
#c(_>5<=_K&$LG>=MEfkG?K7T\]nkq6MLB#itt(V2bDl);1*C%T:]D\I#,pW>U2rW7;c*`f`Oe(VaK[[3.$($Go?X,EVBBZK9b=-Y9pLQj3qAp?Oe_52
h(N#mFB>EG=U-c=O(VoI/MsuFgS37"D8!LXa,uP2'Arj_>tEsmcDQOk9oH5DLbM)hH^&Ll\F*2FdjtQ];/$P[eB@?_@PaJbWjsdC'P;rShXW2O5@PBY7
$eK$qaOUAoeJoI9e,*3\[u=lf'MuNV8P"Wu6$76k#(_kM6:TBECe`Z?:%OmYT=@]ud<>):WA,2TiXAd$lGpEF68&%@S90<+r]G4?:+G?UQfk-U414f@Y
l9ZG,X*[oI5mpps.fO7lDsWZU)h^&C#/iq!1<)C<jNB%P"MFBTH;QB=igZPSc$Or)QtO7[eThFI/gD*;2bGd4>&Ms8JO&\a^G?Y-Q`;rtfo)`MegO/Vh
KL,,rri`:?Ko?#5NBaO&J<E8A`X<*Gg\u^NkP'j+id?g7u?qi]fQT+nCK>7$5jXP1)QnnlHBHCQ%aq:).$G7'Jq,Mik?+=7<rW+2SfmO6LcIKdWn.nLJ
m[^G!E;^tnoq9`[D\2tb_AUa7[4C&Fg^C,dN='r2X*.JZNbBKt.!3=E]I`72&,YJLchm3-'YtGHlrslX]A-Z+?m?W)0!m0[AG9jU)4H9j?HNsOIE=JB\
f:n6SU2H$&Yt"b_kg5<M#FnRL<[gmGP>iPeR")mG#:P!nb72=>Lgbp6$EZonrUD4G6'<'*a8gGLN[WlSf`JAJq`!3UJjmU<6Fl^d1&$V[<Ul^gk"/7Z-
2ToBYKhmN,r+F]_Rf"i7>VcI@bYs#L@`GK4YnnnUJV'PcT<Mf"M1=:<W?*\LQacA9^0ub%_22Ac4%$Y*,[H%s12d:=;*OXJ6]u,^.^0#.2bS#'004TZ(
7gDX[amdPdnWCdYs#)!NL,&Sm?P)L;#.+lb^Cjs33[M-q+VhfDZ^I>qA$rm-BOCU+"`Z:L7YJdo;F_/(@.U\O->Y;*PEe&/Y]dCOB>='$cIJc0ogrX%D
ON\EdJ7<4WJ:3(U#8=4?_XYd5)H_cQEmD>TkLN`tec4(=+_n1[$4Q%X5Z[3Es_UCngLph@9,%_qhEXn$+bMgG)nWAj!a>iPJf/*a"E391H38-[!O!-8j
D&dnaCFpYl>:u+KmYCQqQFBD6&#bV-),5i$b)IP;En*Y.R<\s%RTEfc&%o!2+T7n]D2d/:"U%:NCl3f?2MRVLR*9<"4=eO[s%mbUBjA',]m%o,IZ"=;r
V?Ku0l07!MAMAdH+pX2/MXYgBiWLmV_c4jaIS!bIe];0I-tD=l$9FNdg^+7qgmpRS<^gk!P=c?d`!lf$k)BiiPkOK($G].(#jo`]=Y\R!1jtp>*<9s8'
k0gZ:)AI&G2]OIZaK*O$H7rIT1sEI\`,&5n2C7,64VPZt\71)[o<iGUS/BO/t0RiWRN#%rNg<3do5'aRR1=m(T_B%G:Xt%'+u^a<Mq$Y9:N4r)"#dG':
Yk%!:&''MQnkbr,$Yl%-Z/@2eFm!1hd+CR,)"aCFd!5_m,)Cg.Gum!HlU]FPUs/&\#-c^NF[8,n+5ElC[\!$;tFmJY[.9a>rEW$[rcG(l[1=X;pHkDm"
m@!Qe8KsRXR:O]e][]kDS(csGtGE>AP%cWH`]8e\L;]#]*Q@;!AS9=bqWbbZd$;'l6g:;Q\^*'^E6Au`fbX_T8-L;/GFY@c&a5+XW4Z+M2<<Y/In-'%R
/!.C+Nt#kJNk=>dQ!$Bq%Hn^'-N4=Qq-;InXPG@c7P0hhY,mnu;=bis-TqlY4LLmEpgO4E3kTrqQp^b<+^X)2XqJh6r<#.1dc;IC$>q"dcn+bK[cbgt,
p-,t2UUQoAbsgL53s49l)uU.3_Z;B5K=&*bn1'@VD7(8%+=fa<@']/lBOD4U1TWKItP*4:"#E!R0`ORJ0]^<flM'Qh#Kt?TY't<>*KrFn>)\>X;-Wo6R
sI=&.*D[/SQK05M?3,$nMGua3,)X8QfT'kO/]k+FnlUY/nYNeW?4e.To4##pk0Y7is,*m#<BDmX.$b6Rsr:qC^Lj-.BG@;`;_<!/L?qn3d's"<>CI=,.
SnO?&h97?\<t$9P&bM!n<'L*=O,3RAeN"$jS/B%3g&(&LoJ.Ka'*8X4aTM2`V;XHE$d6UWH#8=i&#36dhS0@=7Km0tFic6:c#9jo=Tj#6^'&bUmD1MC<
[^d#Xt;'6!>8C;LqJq*P18W:a#N$20R*"*F1#bJEO0fSIo+lsi"MmGG=!"V!8h85J>cNsjg8cZkeKR1Xp;RGKsYbX*M_/pH#5!h$a0$'bkj>?W@:D:Qb
0%;7S^@R)R%j9,)[bATRICF\k@Nqj>>.+_u'GY1Y@5ku"3RVm#MD0O)L6+>Ar%d)pbc4uPYo$Q>=b7ZM88F<LOf6ZoncW:,U25?L@$Y3ER1Q&dGKBqYH
W/]60XgiqA#TJ-_B+QQ,X'T\*F8C.5P@rP#jPGYP)t-.U0K9R1W_FZ.s^XX5OYsUdsJLIORSD``2?<gLonM3%`TK;U"T3l$^_P@Bs[s[@U?K;*(Onjf'
<NXN4',/\2o!PB&Y%SgAS=\d-ae8-0*$0$gq.&+Og9q\+#n>H4opP70&SFkHNJtmTIM00X_^3C#0rD[Jd;]NNnND4/;&"lu:YmK[2&*#IU@PP_DXs*iG
YN<H\\&4>ene`XX0!_ra]I(=N]VSOu+]MLOkBa>'`o+c]Yk*\C@?J\e#6<fhsH=;A>:hC,mJ;BRl.W1NEH_;&G41f,-EZ)=@uWUf-?1C7M#$/dW8@'/R
6ngV,kQ(:2fS;K*=32PZ;AY.R_<-@VGfqG+KXo=QlkoJASQo_B#Z(aK7@s-s?W)TCJUU-gO)`,E.0*Jbp4[U1)=@BSa0N-#eafn9%gj=!\YY.!R]a@hj
FLfa4Hl,0-l4-bVETqki4kQ-19VBPW,6A[BXW!970HYt4.bE;68e&]&TqGTMX6.\7`S69TP^#brmM4.QQIIK=b.&cglfh]68;m-^-3,3'omh]nM':=Ua
[^>.dLlb)^Z0GaE)I5_/_=[K`U;GcVTZO)aYBP=@4LF-;s9%;dm2QdC8lMp6395F;#/,i]ckOE%QjP[E?,8S&MT'IfG1ucF-b74Wk#9=(iB@9c%Gp*jA
8>H&CCIU5XZ;>Z<D$`J;)kt/&-'RPpbQ^<NAR^&<M;_9LQs@'*4bd0ffqG"Y^B#Q=r5EAZY^@dl4"W0XFlVBV/OIO/1&-G?,XqG+F/qf<r62[-\HBH\c
nW](Vfc@<+1&fqf?*@W\.!iRXdeP@.Wr7+R7sf&@RKXL\Ku@^Bm?46c-377Ndod&af&ZrBb`gfhF$6X[Z%&ij"e>bd?CP#sMKPm980r%[KZ#/*H()$4E
C1EFc=^dFmIb=Mb9]D^U'E7-nf\OW4*cfLU4G+5Nb2]+)]/&kFKkElhFi8@3%[(M"!mXZ/tDr^dmQQK4ISlP,uK%FR2n?M_A!fGXVC_*@Ud9R2&<L.Up
)*ntachR:roU!J)eCuDs,RB[`PR^o/X/ZgLnBg2gR-)Z8Rkm/N>0mj_(IH,d$riI_D[sJ)51VdukFUM2>$9UHcFZR9`UVp7nO<AZmpU9SJcjnHE6lke^
-03?E.`T=5I^=ao_oj-GYo.bASI_i+8MaoRJ"@qb]?j(.Q1G'>qecM*]1kk&Cm`h1u^E/=qL9@NWf'%9YlS*0pSg`nZT!p8#008o]:]D`[1gWD%a$iUB
riY\6F.)d2-uS>a4m?5i'=nK9!<'$+"*uf0PSYra7B@*0;*3<-Zch'sanZ/l(]^;aD)O*@[0:@g%2JZVcmn_re3pNuq?4C<Lp=i<-N"k-E+)X$fG;n^s
YgqZ.g>lm77/rJ8&jM-"e;8"L[PZKJfi4INjXAR=qaCLE0)!e"eroFFe#lhI:1SCgeEcT5,=U-[KuG1\C@'C;Q5o;pob7_beXH=0ajc*<N&6[lS.=[R[
MQR<3)?Z'C<d9eoM,%f50JRFN.O6!pk2u5$Y^chJe!1:`AMe)\b%3@DomWe1)R(("KM9o4]$>_-8D1L/tD?(Wdne67`fUl@?.kMFiJ)g4(hY%m,JACGI
BD-a.dLb6_+%U$!e-Ba#Ie#@K7-m7@IeWJeNc^oH>_)7CQ.gCo9)?r\csk8iVR1-h>!I/mK6.W>li!l$#BjRM)>V)9JE-7AC-Cmi'iWDfXHocW;fd?gV
Ve(CmZUrLLA)VfMR@`cd>)S5dq`1*Tq0_[h5NB@C!Bu=H4K>Dh!7__TD["Uau/Qe*^R.M64T$61uqA6k!Ms]lba2Bk5*lsAa[oCF[mTsp=7V"d;r5J61
?KmU,"o9NS+W\G+?^iI=6]D;.4IeZhK2%`EYRqT$V:s/3KF@dK!QnTu=K;+s>HJ!'^(Be=P"7##UIk7sE8#:SH<RDkZ\^j@;e"V1RQnHHNuYHd&Mbd\n
`#dn">MrL,=@B#&(11QBZ9VdH]>Ih4eVq_p5)7im@Wa5Ej_*X=eJlZacgX;XN/">&>VH1&aVMNfNV8or/(7;lK'dbpf:#:,Z=)/Yf%8Pb_,U0F_8JOAh
R)Hdg4=cfQ\FbR1Rg8s5gq+a`R4*L9mX@!![YmU%J<oU`#iZBHsJT]TO10j\%YdA<bI1GlEMg!gU8YSTXG2ZBN.:tCr.P`!t4O4Q2'oX2K*meEW6&^R*
ZoVOK@TR:M]T9sNJJaHS<_p>Yi`1I$Ch'EQc`!ai`6g*CG0WMLbLR8,\uKO:5"uC-VWAa-W6`JQhX-lRA9sX9fl7;T3>186pAap34s-DIA,Jt;%J=]jK
9)P>:a9'PrhB8:Y>IbY-fH.RF:G01XMCo4PA%ucL9h.$=F1@l8BPFU;$+uMllmH;aC5<B0AVY9$qH6f-tZ'f#>K[$AYr<hFpeGY:;_$[BQ?M/Kik@Q@K
'GE,6JOa"bmoPV3-A,IFL6`,HEL`m[+CnqbS\%!L,buPp6PZ]RK:H=i/$4>S5Z_'"nnSV_^BADohS@$?m3AXKm4K2V31C6*:&FYYo,^-BelP6!](Xju"
T`IA4+pBma?Ei:PRcqe4CuAmo^hXhYGoq@H<'`Ai0@QnZ6Mnnao)geI2ES?Nj4]s2hp9b%^B9+bEJ;s*iFlI"L^)sAC-aCG;0`C!.Acu\/n>,4<@dT>2
)#''YijDG@1>co'BAp]^D$Ae:el?shC`oQGK6F3!^qr05a=l#eRZ[CY`"fZ*CD!4qV/LeoFNLN,F[eoH_K'm9o9pG&9#KnQ#-W6+-%%5ch>P+GrY(())
JnGN!XjK24p(?q,?jH+(6F1.[ZS@68$"?gk2kD0$(Mh9-hcD%FmcN@cI-um7rUJ4P?>E,5;Z#-TBGEmF)&qP:(Z#)*"ZQ<0Zknn'nh^^YKneNRnjd*<*
eH]2U$j]bmOW^VZWD&NXAVD.<JKDq>Kqk[m<>E/MsJ.FrY3qn\EUX(hf;Sf9*%lB-tSJhq)5"tHk)`.EUB<Aiu1`aZeX#O"r?,t40reJnr*em(cRcN-e
Ne>PZtRq:B(TEbGO.LG2fU,'O+N,AXpS/N$rXt8Xg7a,(kjjk*Th<T:K:t4c-/YDE3EVQ6H%?R.dr=(@](gG=;>5%2BG0,u[^0Zoc[%<igX(#CqSON<C
,-FkS\F\'Y:=^5k+L[?29TWs[n$6*%22Ph!3H%%gOrhCXG6hT]Vb@a$:f@#@tWbS:G*K=\\^YW^X6j:m&mA+WQk+#SYloCgUYlYSB$EF$>>.a]&HXA*Q
We69A)E;/$hg@hQh[SdA&`MQntVg>4C[*:_n?M.,fB.;q#8.7/C\XBP*#2Ws]Nsi$PBQ*?(.)/S\1hQgb*7A)a%csk"7#*.fq3^-GF@b\LkL878%<6-p
ZC.Pqe_busHpt1gA\7ed<n#r3[c[H7"k]X7lYiC^Y(DkCM1?1J\9XeF]""PgV!ttJ`UcdDO],.d-@I_$*LHDH5_u>XgVDnIL?I%m:P'^+?KJ;*MWlN,`
Z<\)#s9oXl3OeimRZ$;k&[us$6I<Q82`t&5GFnba2H&fVH<Va%YaKo._-Z3H]St[61@s$lCk51HcQh/n?7o]^qW=<N7H;3YEBl(5"StjFQJ//]+<G`>Z
7a<:?,$$Il[mC:1h?=M'oSQBGWi)(]YY_c<95l?5cQ\o+B[N#EN"LQL]9(-p.NqEL!L;gb/SkfmubANT`$E6^H]nLp'Nhq%QtlgBlR]No8cLmg_b5/$`
i76O/u9FD.$n1;&S`dYq,\4,Z#LcWua&-=\Sc0^p=RcjfJ[_(F)D[62f%`a6sQGU1sjl!i^B#eg=n[hiMb^Yi+<DUb/ud;W4(BJ]LL"\/BpHc5Bf]o?#
G5%_!JJ69:46&,X_Fo)[,)1>6)(\@^)CC$tO*q;D>Jg^'jI)N'.HMQ%/mQ(aMf)YY(J(i`Lc)hDm7i]#t_$nFZO0IFVl]0?=Dq1.c5$FRjZb]$Mn<D;F
!ilJ9cA'g5M=<IGF"\h\jmVI&e,t2.:UVf;GUEXY%p'KPg=DTmdOd/?8Ys5B,d6VK]T\F71l0ZZ2fP!GR`^6$0(X5QI__F(KS(q]4Le2!rc>^^-Jo_bj
"i?ZFC:"1=Je*k*C:>4+)N^GN`p%(o0%:R7?tJ4RdQ:b%JcNp@<_qGB0D;AMh+#c!a0=D_1gZSL::G,P<n.t`k'QNn.#jkCMD9MIZ[?-:K9=#52YR/o!
JVIY3nNg0SYNp:.L'rT8ki5Wd"3p"--4<e<So?_,%>:#<\JQC$DeE;C,D\E:.=\K/5=ID-]JW3&0;:#OK3LQj[YXNcG/Uf^kkgU#UmQ])*^=R8t,*qRp
A5!jf-SBh'T4),lD5I`KeeMhgt?h<j+e,+"$[\8LnF$lN,h3FAV)UR?+R$M;:ZD:+)8r:]XN.fRWE`R/6R)0_EKn;pQp994SprGX6=D-Zqt/\B+T&;U*
8ii_sbN?bu`(B0#8JQQP<Q<;!(D+VHIY,WI1jetq?<0f/'$B.<&"A#6m!XKPU:ZaB]H_t.+4gVHpALTW@=iBaRUSm;2O'dO>"O.*uP<dG2cjIaE,Gm7c
"d?Z@#j$laB6(=A5Pd)XbK?iD(l)kT18KGe.$'CY)MB"j]I)+&#hRFfcq.9CJaPosArt.:E`X2C'=9S,$FSmCO9`3Lak:tCG,""'qtu>%p%6_agatElS
lWXXFM?R7;]HQu7^T^=QT**gP55q[1'X;I:S)t6<3't$f64\:bX*8U\%,Etb(X2+Lpab]e3r];**tO'?H8V(79&<dA<,6M^a?[H$/94F#?Ls)l%h,Y=4
8CmR&lNmr?/E`&";:>;m7XGWs/(sX/2!t^9@SV@,>Q9ToNW8S3+>U)13a.*5leA<#q*nGNF6`Ul].;%XhQT*BQ8V>tgED<>/)Ca"8`CVaN<j04?0l8iM
99D0nHCAXF/(W*Z5`VS/ke%THE)o20Oh]LeYph0_D;O$q!.G)MMD@QA7"`,U<O0Jga'Ao95H_<28WL=74\JB&3rIF8Ab9E.DoS]D&!nApfa43Qk[5Nka
DlBU'enek2+[[Zb<]J8H@n(S(L<fu*e$6fZbrP:4gob[:;0F2F(C:ti-n@FCm<Cg$,Mt@;$aAC'Fi+rm4lQ$B6Yfe*W#/%:]IRVZhAUQoE%_*\q'N"Es
#I7dn,sdWu?*X7kdVM0jp&cu'n`aY7EOdrr6tJEYO.pOblM.l-*B)a>c6g0E:9>ob!5Np2J")Wtn+b4Y527,!*d;s,IXH<`J\MDA*tD)k014csFL=>_5
'ZqknWP?>L%k..I!;UId0iHCSIdmpWYB#/^G'IoPbjDtaKFF9oXeT`_h0M.r?j#b\XtOYc6eHPl+d/Ar@F&7Ec['$Z4$YY8q6Ykm?4+:7,f5L.e)<H.t
F[R@8FlXV4#!+#[_Q$ioaD'@>"ciMeACJZIdFHBo=9V@s?fiAs:t>gTn.fFYDp4R54NMo"3XD+Q7!tAf(%8,0`mEpM!g3IBb92DE8[[n;3QJW_s#C"-t
>G0IC=P$B"n'VR&i79BaVhm>[g;`<RPa'T59qg3^),SPBr;_)X%@ftsIdlY+D)qiGJlC+ql]!&CT)9?ckXc$YsjMokYVFHR/40TGK*\U!8gg>$=E^e!I
`?#pRE%1,(N`^0>b`_=$bD?)N6,jD`"(X!OuJ'C9mfBX_s&QI$SB4*Fhlg3EfRu4gUReQ&'DI/d\jCU`F?!/7spAhQ?Y@53)-Scl6n/sE$Jm49.lF"Y*
T+&'O2lkhKAjbXUOUS\C>'kF,:10OuCiMacZ+V^)=[58O`QW!%Sr1pp\9enu'k1"u?Oqku!35fRACA>)2-Vjc@!Y$A[(E;>:h2g,H**<ZnLg>aiLu`:F
E`N#!@29$(MEo;:DYPV2T2+1;hXsW[LMiR+p$*hQ7VV7B^$YIejpQ3BCO'h&X;4K`dh1%T%kq[J5qr@;]NnZ[F)Kuq3bXUAE$&tZQL(6)CQ*@GVhO[AM
@5De&c3&qEr6/_D&AL7oCfBB+>_EUW-i?ds$K6[:,1-#:&+JZOWeM(PXke?bZ>t!>,C3V*Cc5jbb6_Gl^cn4I4V\B&q,>p0,aFT(:dK3DJ!$`t?gG*BO
2O=$JJG]K%!bpYpq%,G$bi%/gb_E+`j>=95"gFWkLCJL.k^p<q/=6OqQUE-cg,Rk"4\=;\>H9(^>BpUM1;^.`pMT0GlI21=-#-!.3\'I[4(2@PHHUTgg
/aT?*#8>uIPYFDJ%j-#".6t<)p.=7?!"Pn+f7:X`M]nB"lG\krX./,gmlOHpLW4:Nj!?p4?^/5IClq;Ea;f[R!MZ0WVMB\+^WJsiZ06f(jR7$OEj&7Hd
\0%.U2iC?#F7jO]EK5C8lk]=HHnH28>82Y:f\W-_a6%Jf/+SITfl82*oOcn[!>OmYkBKTRM/q8*n:#FBFU's+4Oq)NR3H2.WXT5&X)]H.KKfCD.Sl6oO
rYTMh'/!`Wh\-$esE][$DCiVRqFj;.Dlo;\?j<#&aE]\MqRIFJnc/M1,4qh\\2.8/X\fLdDLD9e;1I^\MKJfROME$^uX?6f4`on6M=MPPefS=q5B!T<m
[7gVh:p5Aq<f;>EXgkfK2k/7:'`X1Z\.bZjoQ[Z2PKG+VT!rAWQk'0QOiX]=g:flrgHb#8=LaiTFJO'k1d##7,bLAWeR@s4b`sGk9P=Y;=#eb69DH_>J
=#"9$!MIeURQ%<;!\-ua@>.)HcU4aos\pXs)!&'bbc:/,nWY>5Td>0J"A-O>U/]_R+IekbJ3!Q:'SQ=,O5o7\GPq4hN'g#N0"<(r[YA'f=/%VcStj(/@
IX0`85]j:RHPt@OIlm#Z&IdEK]G$T7=Oe#Iem1I/:O/qAQ?!XVAlG.mQo>F<#XC;podFATT1k9@ck2p]?ehq:A9#!OT=)Le@ZOg:Kfgqs[mnN\Q,KaG6
J4Yc--0CionBY7#BdE!QMo$/'W/L@S:dXIDl7$*5]VUWLO3pH"Y`.e-i7rL4e73$sR#VaheRCTjBP.Nm2JkV]>:!BO2/I%495LYC'dZdb%1+U6I&So_Q
MQY(0@P=RW7SCe2q*R/\HVOi>e!n8V);<Gqj/CRq<@ib18.dOHk/ml?0$BtL;3oJ3He&I<hgCbK"(7n)(f*0GdrhkV:,%Jq\D=B@b?=sr]MeL!J:iR;U
f6F+6oH;`ric*<EP<ZEYNH\Jr=G*?(8R6qe?RUlt622kIcCl3ULj5]@rXkI[D,"P>QP&RrNmrGBI9LI3bZ#X?#=I95oRb[p:97/jMPpCj@u,UoTEcd\R
)R8g,*#gK]W0W,DD2U@o9KN?-\,G('F=\?k"H<MfHW45e]g!VK>)PquXgYK]gggp[n(d8b'r!7O0%C0RpNjZ@^tOMS.V!J;s)],`c)D"9nsK<j-GMr"M
9:^$VW.?TKGS$jq^_]3#'I6[!D+K)O*1Z8@imL=8^\t)XAD+32]j*Arjh36eVLXT,T>Uq64h4pL<%q29@SA&H@h*W=lWKUO;On@`#=OQ0udjIBXnGSP`
:C#beSj%Mpm!/$<$CW.<q8'fS^]1Pu0((Xl`SH7Ds7H<e+=#C%rcKF=m@B7b1l]KAa:37YP=r#Y.ur[#co>]5OU:/.;*(DbH&MAu^F#ok`de_Eik1YJ2
+?J/&)gl:`\Hpb0Y$aq0]dCS73IL"g.<$6g-;Zo**$.qB9is13T,M4K#qZOMn+>M'm6frg!tJT=C6/d`kkjdo8<C)N]F:EX/h^I\H\faj\Z-1p^0Q$cu
<+ch>5>S@&K'Zj-,ir3tA\Ujgli*<OQ@rl+8u$/_Ep$N)1%'e/>WgX]45f81GhW-YW&`.&JeNW9O!Pr?n;7"4fEl_`2cX80u]9#fB*BTkt<CKt!IU1VS
11_7CIdE5DlO/("]=!W7(bSCuCpYA^9n(0N5$ZSeT;@<hmKeo^:ol'N0PS2@^_el4_UPq%("`+UjV^bWr?3$s^.H8?E`/D&SJFGreT1_8NW>bDJ78D_I
Rnt)DYAkTr.!j(GUTO"rQk@S1m/]JcRrpo@Il_Fa.T>2lBU]:J)>a_)[o"q1m%jWut7b0j<kDWo]LLr#f`?2<^&s7s+4JaX3AObf3SVqu)qBKLrqIeit
/]_4`E"VTPU&Cs$/$;[A5q:IQ9iUI'_pLaiAkdK6L>>6S&)FU\8[W]sg3K`=Nbb,N.p0H,(Rl&eeEZ]3l0";,_F)!6obTU#2gp2Gp'ngi7X7i2U]B0Qb
i);sgdhX><uRCs;1s7"q@<())S'kSW3gif/or,1cQ:kQ0`,h[5m;uG[^,NQQX4h@N^HR5.:#be=GuZid583.c2o>]2nkRe[o%bA1l%=E:D=,W"(dX?)8
Y-Z@m77?(2(iUT@_^"!3-epWCa%KQiHmHK87(p;[\p[']XL$8l[DV(,iN)b$CGpbciGI/M/t[n#$ibr8^QpZWX[W!K#+>bhmba5OTTXc2GthPMG,rW_r
(Zj!)^s=I1S[*$;6m*BRtn,1egpZtQA5rh3McZrKo4BIn>pR1sf9Z^S[hc5n`H>qrl"n5@<O;uriRdWCJ_4gUPZ;C6874Xma8f"S,Vha'k<-#!e.(??C
d,h'EZk+h2.IT+EhF<%6%;RIYmT]Y&]B#XEG31*^(a[^DBG9;--_cdEh3\$MW6R-/"cY)i9+$*LK#W3Mq!0NhafmW.jiBTC<3W6@'h"fWD$\8OA2eUkR
pZY[XJ.Y(Inl'IRB'fqu]d\@N%S#?As!)77R\':N\/^dZ+m&D]]QjJ*S%!mjYQ,4o/T._X<OQ&d<WF='k&\CK%!I)jFI4/2$7)i7?_)$M@;2q%^3K[e=
)Zsq(Xq8GK=c<tn)h@f$O'2*%bG_HI@_JRdgY6\`IpV8WF#>)!\:'n5L)Z>[`>e/@f$RG8,[)+KZ$Y4o-eok!j<4I=laim\r[r_9O+32"t>EOTes1.3@
`"]`P+;dlein0c\LU:2-TmmL2NGeMVdbSZX4bSU<n-ajH>Gk,1OGY&,LEY<!nr@:"X;9,:l4NI`GZSF5Q(9kl\L:6q<K3KL_Dl*K]Ll03)@;3(TVQTe@
BB[c?nn,JO((</Pi\ae*a#3i6W.%0*?!eg12*A]OIS]nSVJ;KURG&amuDH3LUWAtR/fTX),(lWe%KLbbt&V%XYF.*c9CR04BD1Glj:WRCQ784A$I_>NZ
aZhuceQNVIc]"OVMlQYS^o+AMI[Fi+uN!CDja`<jNc*_p>[&F3dqn'uDo(DoqQA5C$W:XM"%<=jW:&+47Tl?h;W$Jij5rK*Mhm]e-WbqWTAp,UjkoBg8
]1AiS35#3%D5=%'#$XDjEh=MYn$])qVSM!9+n'Z'Ip`<7?S4RWQi7K3nb.EO4fQ=LR"Np7a^TLin3s#.i-,M-84'XY5qbf5e#u($!(`()r@edP9`H5c5
sJo`XtfJ!nBE9`K-6X>;d$"WB="f`SN2Vh_\9/=_aZ0jdT!FN:^G.\KAP&GSYUFh:.Oe%_b;p-qg(X2.DE(%,6JQLd0!9]><-?,2Pd<;G([]7dK<;]"`
FZ1!l[41e"Hu_b]t,(E$<lA#.^?cktK+F9mS3WaN].]%b+eh$eB'Vr:]l6+.R!>Z/je0DjKK0Ar$P3m^Ob/9>l8LX(pO[;BBcEV+PQkVl!ut51d=nEa^
oL?jW%>L0X$-T\E&l*@M$58mu.I-+,T5qu#5-&drJmMClMi\Q[o;iQY_:\'HZSS&q(dF9g+de#eX2n;X.c:ZlVm\&anNXj9.)]W@.<i=n7Nl$geNBR^A
d[ud)Qq`KK__d$GX8m_$4ZPX/7fV#_);9IZ_:"q_)D;GWXde'p5e1@gL@0UJmN&DO=j,q@DUb1<Fb3>uggW\8RF(I,=D4@8s&KZQIG!gm/[#X-b>lh5<
>QW_l[8$.'CBM9AjVEAG"ErS7:T28Yc"dN2=j([Y,QUf?IC2f?TA=NFG^or_['MW6GP,os>'le'V&SjUk;G:^=_r!W99@IT-p4)en2hO'#!O0qJJ-p)^
3"ahaiWXHcuqA")FK*Ek*i\:C>V<kB"gRE+EGMl[-I^u17:_c:AnlCfGdRA:`uVGXGGI<h9C7'pBq2.lkhRkMrd5;)a@6\3I%apVYbbp9J`a#.*)CW*_
),lG?1C#eTG:j!;ETUAZZnFp>0=@okY\kB!>G^A/:,QM3##M00VC3J<#C$#/^g-r"<&f*^^M"Y`l(+!EcDA:9A!?*,b[3dfYa+i6``J\XIrH`%S'j;Ih
bSA>jn7.r2&h"jf+`mmjLW*=@]FWZjs0GmJS79F8XXosS&poCFmZhCQ%]8%,!obS1W5l(he0r6cLOA:[GZ\W0B6hqFG?f0`1H/7'D$FhXC>_Ia07IHIi
s$\M>m((O=E%p7ifm\c[ar`UX]PAQK]r9D1%4f<,B\"?bJPXWCu%g&^&5559E0VDN`P#8VUpsme=.9[Jl2/aQ/DSeXtfJjAl`lP,_4AB9-A_)J&;<Aae
M0=RR/&7I3D.NdQ9b4M_NZMu,)Dt?3@3n&"Ieh3N=n3h'ZXBGf6XR0*.mSKU?RXo?YQtA\Jd0=_DpKScmH/"4VQecpJr.d$3Ns5OUONo`%d\C<6-=_R;
0*,gaca>p[$_^FcMtm3*X,@GSRQi`Bl=)hJS.]78YYO`q8E]J0H1S0P2"&/AA33K/!P1o7[7db'8"+;`%)3>[ARTY@f+]fQaQ#'[VTjq'n'V065IY2[*
3t">@_Su2.ArD?D.)V\/@#BT#,63#V$n,7%"o\'QOt"9q83Wi1G(:)bD*)?18AtSaXO)E.aW)9Qi6.8Ce%N_D<#d>[Ek`n:,u/UILXtrDer_19YY)RBP
.U=Z2/cGD4Ujp)i.sbG.@_2L[GE)N=SVG4*<YZ&7ZEcpEE>*PEJ]i-(R:\$SoFFm1'uC#SbFp$JZFk@X8U7lFE:%r$DKZ@RHQB4tK(R6O3#"d/h>Y$We
<]528QE]>/[n8rGpp7^AJ]g*VQq9I7*bcjnY?T><t8Dj^kRhS=nVUo^KY\+O@J[OqmV34"rHcG2_[Ljo'^!992ghQ8beXhB35Z9*OfVK=WkH8(+iKgmk
i>jj7*/7\"klHZJWH:c6]s>&eCtkYm:a1h=PhX=,5LaS?`Li3<\BtEum<)<S:-5M7RP!/.g;_4<CT8O5<^jFT%m^iJ%-R[mB;k/1Wp9o15O^!5dH2jC1
U++@#O8R,-L#=K!_Vme/GVQ]5.1^P&A6EB@qn\/M]>@8Yl7hU5Rl'7@_5dM?^U`Jem)"q52La&(:oFWo'B<P]bq'PlFb^+n"7^T$U5X@GV=/PW\%s1=I
V58Rhf\9ZuuajOSbolG_]:+)5^<,H&$q@jjUq-56i@RCA=?B&?a`tR'CS5A%KTAV[,LF>7Cng`sq^ddL!KgA>=;Q6pT'qWLQIgejg<:B'[AD6;?rZ7^f
H/KsZ'0q+i2-KnLc!&@MUeQN4TdgaG^:qo-h;;fV@Yg!GOL:>SaW],Wc.Zd%c3/*JBA"FqBd/r]I5%t8e6*df>n!TnVZau,hNje(mVs#!;RF.X^$2b*U
463bKVZ@jBHa\CLkE[3\Z%BW49:NGCGRqY[S1g8L0=-o)Y'4YeM!FA;.AI"`Oi6nIG5HT-.r0/%(GDb34\$^GDGpB2BJ/knX4&2j_W,Wj,pqR?R.%kP.
cjMDLoq6A7Y1\gAA(Lbh(P8HFMLiIME"E8c5Ir*B;A!LD8S74M@mL+TM=HU!7Vcd/HE)r/f6C9$',G"i8$2MZ<q,,d+F!S6dEMQ*"^Mt`KLQ]%!'rd7O
7(!J3uE1sZ#LZoaKX_N3WsApWFo$q9\^@68h`)o!Vg,bOB'=W@9a%;$IhhRQD2uka#;CkS>LbVhZrMq`P*pMpT6E`K/^*(,gr0$Sb@WL)8r")K)?2uE\
3Fkhcqmj=@3W;5B,9#]j6E$CUV/m5L0,9@j`-n].[uA$bWQET+eGe[oR\Y@P<GT_bcSlSc";QF'k(,)EG6GaXiZ@2n-?*[[jbH\sC%iXM2W-blpNe,Lu
$\HojYF`ZcqE7Yo0h'P\E^ZcQfoK>]JaJ=2BOVcN1=Mk6.iDk0rYe)b[0NLCjD3@VTX(XTnV+-/AT275;=#-hIRi*IDug3PA!Fe+o_IqtU?j3G7h9M+g
2l$W;4Fib]c'#1<OYC];d.0LP-+KrS$c"p=S"gt@-i;m@tP=g#("K1,r_!je9Z?F:Q:cYDAfoRXL@QVglrsl-3IMb*b^3KOuqfa]#JE6`V$6JeN)C=;*
"tEpu'$[BU:42tl(nTO=$^@W<Ye)hYGE_a:T*>NllOhodL8+h'9rmd=U%-?&n><B]a5\=-qoJ^08N'@cE73mZQXC7>nBR9c?&=b0%I==@+[.#IZ/77UD
eA)Zk2#T1K8>,M7k+*@k9GOu2K-iCj#=>t_pTTm#K[!M`H;CdnVT/);EjOjO6ZDgW5\q9WQm14kY-#k*F?,VPnU.5pUOe3q5Pp!1g&MJ\aImDJ0GrLRV
WI#7s@QEYKfRlqQ.3X%ta>XJ`J5@Sukq3[A)(2*&uj-!ogO$ZNl(O3\T\j1Rl+_IN31o.2,a/s+H6j^graP3Z80[9h$hlOiW$4"p[\jH47p]PRT3_7U7
/j+>qA"+rdlo"kkS6T7;=2m0?%pjtJh<i/D2tVY6*YYk(HN3@aE<8SW37.L<T<p92COTf>%"=D@af_P<t+<VU;TC[Y2HDGqk]/Mq![8UjoIk"qb2L]b_
ofc,TIjGd<A^u0Ou`e)mW4sm%n^GKfP_-n--&XO#0G)BqMRkZ!tFq8.R/6#9^+,V_U"$`QW@/6?4>qE^@AFhMRnYYQ`ZJ;U#6^?AM(m3iJ_os45;a\Im
WAu3+lsdaU,U[(!93+a:A8+O-n*Zk8_B,5nB+&!U?C.Bo&n51L+PAY,N>#JPV?>je:9<fC_VQ-\nls)9q]`9Y>ao2n8Ar+mo\*QRVJnA*\)i_OZ"OH'K
V`$mFP'ZD>bB`GWn^EAAS0>^]t4Em;Qq#+>ct*/$[t5-i[ftC):?4n8XNLsVX\E3puK1:9/4NsY-b&\*70PbkCd(2g[qI:Acj^nMUbkJWVpLu']>%\R#
Rdc$A:t[D/,h0f:.db5=!EY4"U?E4_W_]ZMT9:=.mG&h3XHPn%^U?="J4,)OI+2H&Ys+%0tiA]pP1p#h<8p&l\OoqH`R'n3t]dhG^ODKBKUm$Tqi;[q2
M%7MpE%0f?Y+@I@Wp$j?&I)@0^\=Y1l[l8&%^iqLT!ai0+="F)<"f/lV5/&bZ/?;0*/M@6F);?blj2&V+*Vs!u$,nMC!GMppBqg@d2Q_jcWG]oqE4Km"
>LV56V=.k<nK>A\W#E!D)N+8(a\G.XK0XQ%t)kBkC'Pahe=BM8(=bE=OaIF<"D/"qBAS;_?%Wjd8Jr9Am]_<uK7?7i_El9-*C#O$LoHFa+f;U#toN?IY
;A0gSd[:BCB?Vue')G:P9mdI/Y0X,t=YAaY>B]4$>en[seV)D;4<g2l71<5(WG!iO@Yr#gF+bIoMmCbtVjE_>R,o<qOHDAc6]n^?o5IM[iQZPr`o-Gm3
*Du@mXZ-H,AZXbK>S`O=@81^7ZjhEF;?.I4#C(`g=(C&I(uF_^:/!5QBJW+O1N^qZdA8Kq]5A10Z$bt[J%Ygjg_3`e^"=EZQXD-aNn;AkJ"E($pI=&r2
%"dKO)U6mg0A`DALc$Ae)dR%hskg6jBqBI_L=uf(Ra&>(59me,MA=Wg:'ZfjS`BCWg>ciUL+MIR*C<I>Ih!5hNoON1=DWT>otF2ZC&'.&gf.=7\&D)[V
&[4oE@tM*3&"-_(Tch'HrCKL<8"eu@9I#IqdR4HI\%s"a=ZgMIq`4c<[pVW1W7faRtH]VOMP/5_YU@nG/^V=CfV"9W*V&V0od%>^l1jCF`R^-L$?PPd[
p@e:tW>A`1*OEU1+cQ'2ebH4uK[r1$%\dMf/naP>p4Kh>:s"Y)&a=^\.)ig@<cG2?NcC#g4Kc4@(Bf;ssm*K_FG`9Voe8dpu'oA'c:_s=-_[8';K8]0a
Ho`@Z_F%:N"0!#.MAJ!O"g+!Zr`C&gX;"3ap?^Q"W8Pe>%udqW'\Q3,"!h;j4\KEV+^Sq+Z^R>eN,2Mi^)*u:ru>#cUI2o%KrEjCKiM)i/]ktK8'e-f7
t=-.A\jY=>"[+M@`bl=b.ECD`T`P![n4$?V/UYA`Ws,Q.rj6+('Q@M[E@0MQ00WhXAb1m;jLC#(^Jqk7_*"fpVraNVGJq>'Rd[]B>R279ZG@eIaCW(I>
VNLX>n*dIV`'P>4)Uk]\O1@e`L(_!4o:+.>*.c3;tB;1^:Kf\YRTt_Ca,*`g:3.HfjAao\EpGC8C5'-*.09>:<Ik'6X:'C6"Lu>-'BC7F$odS<49u)6!
ZA,rQXr(m81mj5bBPnWP=$)kI(i4Jn&)f\+cegBo05ga:IZN`StTjbY1ael"+(IV13SgW7W:e=EQ$Zj8K9epJ=rS>+1I_f^!FE\l,D\X4m!:UW%-2")0
fXARhqA@4K:Z9W<dZt6QE7ljqMYTPVL_$0h7TR`;u.'bKm[=u,.2h%9dmb2BcV>Q&ZLUMP/_ZYbLXPF_qA%O[<O#u5@4F`VFEh/!:YKK$kR05f=T`<C)
o9E;Y=S@&n5p'*s!L"d[m6?.._X]@j4J%1b4qb0rl/dT3L(a<:i[c]A]b5ha_/UAMp:f3C%O)-ONpT01H,U3;VjG1Z-WdUhn-tZ#5qR[X]n'2X\EYiI&
=9of0XYn]HK$DAe'/QkCa]+1&3%o69XSBI]D2'tgK0>4j*lW"@Y0q+Y@6q@Mr$le!0RdT"QqJCImeDaiueu4&7*Li>YXW>J4.D19qoMDO!$2Q0Cp;ag9
_E9,#<a&#Sac#r#9.JRTk,:6Sk7\e^(Sg`)Ua-QA3Uc#HiF3L4'DZ_+<@m/u3FOXFKQEjTOA^QPX)jpFsl@DP5<O)?a4rBUCe$M0Dc']eUYQ=ZHcr8HQ
HW?XC[g3JLm5?$DTr*&TbK!pg[^_32kuWuQe+&h9;e'e>knH.SdrRILp1IV?jhMdmjJV:Gf1JBHFp1q*<bk!TG6I.f=\T3eL!\gD[e-749_';<"7%mA@
gEmRO+G6)?FpQHn`%2h&aDR1Vk_srie,K7Hn,kRjReG8Y-dEC];3<o'Qj_QU"7DqqnS)V%p?,fo=b$#=-(![7.AQI<Q4MC%L+qn&>2"PL1DTY&Id@RJ&
enhkQ)'02#L%HffYEIG8oGmH:lZb>Arf(,NbEgR-?r;+dSihEr_/@=en!(]gbXSOL-tOj6j&.;%DKT8-]QsDNjo3YkK?j'YNt7g(B@i-Vql-im6$;Wq7
o0j>DbU'i<E@(d-0hr:KP/o.M8rHN,.3#WDhWUu..509X)asf\D1W)II3t?#GPtF?%Dcg?-B;0Jj>A9rQ.E^#=[^K^e1#\Cq/VH>P=3F`7=^m/?O^=H`
&;97*DYgo]nP\>qXj:"kj)cCF'%E3SfffT-\:eo.(EpF4f90G<$_^72Y-%KqZ&=T\8pQ.2bGs\lh46P%2YWq[%R=AfR2YF8JZAUEi,;YWD:_oHDe#WR$
ha3e4Ec<XE-<d?SH^FT?bKJfq9tfsrLUBsaB.,sUTI/a?\;CeES"Zm[mE`GC>hR\Qr/qH,'=U8rkB`bI3D3[:co%9N@KRn_'S!$6Yo>\U^4(5hiA/+MZ
6FTpiND+Ad2a=g;/JtH9UME!BA[?n]OgKN%]$m'',5h^AqFo^-"WiJ;AG5JMecB\ip&A"^U#\Fp`W=XDg1o^#W)/Icc%QV'57L=r1$j+l%K:uEsPr3ZB
<3*[")f7ub`!E3pgIuHO5mjHtn`l<[=fP+-Y#B<-K4ufU]Z1tF.`&r$)O4FKkfG,TX)VmY1O`7N-CjTKl!tQoD[ZnS*'1kB%>(j+-ERc;Y#tf0m9`=<<
[`bR)TB-B.0<Y?e5Jl5YT#RLH76!s))rnZg];;3=s:R[$H>uBf='s(70&^ggX91<F\C@d"iNHC6*Fegq+=[iNjVK\3jnYXI1(0IloKmS@l8/B[,l!n;^
VE0nMPHFRb[0\ECe>GTc=efD+t(UmRkYp6JQ6i;.:i?]\qG@WNMn`6VX!_7$0Y@UZ,r%h6aHn/s0+4dOijm75s798ljlU<?=1@2RMslVZfDji^"n>O<-
-ikUC@RAT[g[EbJQ%7aN?rNRk/KQ7Vl<>s@)MehNAs/!phD:R,s@WFUe<)<33SXRui1do`@plY(3:/ML-F%G)Plfqb\tmAinHJ9,?f&qA^uKcF?RT*lm
1MtB`!er9&2a.q"B$>CV"ah6n]@#a)O-p0u\RYkU7M3LJ1nC19i3uU.\K\._sL/[:N?elWG%=9<]Q3SkPl*+$1[TSM@=g*b$f2p%p.'=JnXkG!SZ/B_P
nmu).EmuQl0SLo-jLnO2'Y4MUUKnEK.![_CSuknF!TJn8=D^,IjZUXHN$]/^B+Y?9`_cOl6Wjj-K`fb=R#M>GBT*7dd(o8a`[W%R7cW`9<k<7-),!pVV
'3oRf3`_TT@cWI+,ji.F]$Z@7P)nf>";ejKM&_T?rRnIfEj=(Ugg_)_t]10I`G!OC.H7I(2'L4Y4XtF&KnZa'a-cG>Hp=!m>?"D1[+Oo`rYd@L)-aG==
#cYV%_!MEOWtUQ7o-,!@ajZ6tg!(fs!,[flu)-mg.&6+<Xf*kd:jQW*saP1kTgrY^c<9afu8sE'3N^Kf")4b3FQfSlQlT+1W0IMEF5h>*/[Ri7/d(SRG
>*16B""N[!/l$d9&IF$UX(D]'%N?7K@jh)BR:"A^F'\l`8AE"4qj$i].=!d7LMXb%T<\fRIH+%nOeP.&kZq=4:fp_.e2j",$Ib0R2'J<^?%UV:=91;4o
kVAp>%0B(F=0eM;0P6j)upTg8,-NdnVB"e#Em19-6D2I+TL;q4I?VT)]*f8Jfg;<)n>J`Jgl141'&90U!HI,e%nIPrM3-[\=!:=iJdT>2MhZ<D:bW?4:
]mTJ3+T''OkALk^;CnSXKQ7oR/;:Gt"o7!r*Rp6L)HjO8n,;#0&/i<Wb<^KM-:@!W;<"2Y/uJ*bE+&Vu%1,stMB#Tf*^3qh,[L"G#n3pGZ$8rdm'D6K<
+1k";:90\)4Z`!PBVD?TL&LG+92W8Et6.\DFCtrlNadiBL9RS6FAYd>&L/_BTRokjXq)l!TrZf<ZM-[QO$So".=f4`H&4O&HaVs@2DC73>@N'1o2]<3M
e66-M[_!5l^H_[l4KU8&N4N(@!)TF!o)`dAI7;2>q&H`"cocCT+dO)W5\.*9M8+EjnOb*%04mKdI]qBfsAqN#-^rHL'0<[*S"iS(=o[Jb3E)>;=CM`3q
jJ#FFTU-X;tTO>jUB$8o;+RKHrD/L-Aq=hH1LC^.?o)-sn.'4g<`T[3:u@:V"FiGL?m#I%V^3XAE@:N8.mA7!X#OX1V]/KIe*CR]($g413hej]d6n\#i
.=El6nEHiWi-,:?ZJl<`U<Mu4/'ks8Eo8i/SqucI!$qUXO=B%tGHt:.^0@6iN=d00CP-t_3$a05b?G$7mn]@Ob#:nj@+9?oblZ@;-Y:XgW;b;S)QK\pg
SVL7"b!35tK:Fr]VG_W2IJ;C1^nI1+7lYqdpS!rfU^np=hR+n5h`\dq&%_SRI1\>QO^#^"8.&&X*1$-il(f7T.'M:i&/Z^F9tKhfrOttI,>,Gkm$#(g)
''H3lQ:Ym4Z_V/:*8*@X#cm(l)eaj-Who[3s!WC"W[?WLcfCM9KD69=NO'P\=F&rdcP?dniJF1gMcJDhdG/)B]>d'YL==+a3"3!Uf:63itF@T+uVAE+.
>\QHZ)frO/`Ip<X@U5]BE0abC[C+9W[,7J>'A]pa0`q'pr2Sr-$p*q1d65)/T`-9D*]J4\?>-4>BjlX92*1W`5$.UTArm6^pP`ek:,8B3e^l;3Rh%;/S
5k-e"*R)GK=91MRS[Ztp$kG'&hGZqkf]L5fhe`sZPM5!gd4't*gNp;umTR;NrHkB,FKpCF[76%O,Q-APV0_9u!:?JY/mXf<gqon!O$BYXu"'79^PG5hm
[@V];<gtEX(30CnZX\_EY>6-dRG%bcIJ3%om9/^M_.6>?]Z3&=#0n\lW(%OSR54Ai'2-nK^U'sOMTni@$`DA9Igbf1;"g)Q"rh%egK@*d['!:_J)Jlb/
,o(\[i%FTp^%oOhMA*6IjXdt2!MUbRR@2)*='*8O&*qGA0ki%:MMmojD<6C2I0@(@4^0jrcMm3pMY6`TlT53_4e4QeKYp\!CSu)3U`EM\6gShu]4!p=h
/!%mc8aU/o^_3We6FQ3h;>fQnXBVAj*A;0R0XWXC]d[3[(2B5iH:'WbftM8!\@P>KQ`MQc%t@`dqpEJA/u'Wr[ahQ;oV'8MaVYBGK<=t'PW=bqIZVP,a
<<U5E&4X`-U]C;Wl/V-=40VFm7;)k8)h=O[9S[`_L)\mnV27:O%7?*pIHQo:4j)Ko?*dV],RA>JknODUJKh5A1biX2*GfQ5+9+X"I3V^"s4qnbr=AI>.
Tc-queqjS@\u#ZB[1&AAIA;fjoD%TkF4WYN-S\#Cc11^"OV^ig\R52;]g3tg+9`cC_N6?JPe7Ift:NQ)FoXlcPRA0=1P.TS:CTL#3/r%&>uNTFW:I&#]
$Z:IEp/VsS\K-S)hE_I)Ear3uiD^Y@$2P]aN7l+YY.,0XG8I%a]rD8r^#HTsq\X9!t5r\3^/g7RJ*"jkU3f4YD#2*d`[Ga)2_<o22I!e[][/<'l)N,9C
o3c2N*=5C'4Pqp3RLeC(7h.l,9mm(VeFjg*:*r2b!)I.#*Q/Z:WX1PgW]!_uA0/f`S*(oSFVOU:M3:T",53MnMeN@K@S7Ph+Y#\kO^T`m_\*"j<"$V9f
a>;L4Dq,,?VA'O>cBW::0n=)#).)H0[tsq(p/C*;)):b'W6Rk8Vdjd``ru7`lc<\U,Xb26`,CL=[e-58Q_/4+I7f$e46&tgMoB%3=XAif3o>RB>`5-_j
4&$oBBg4&O<o08;8R[J3@4C:pOB0;)%k0TU+*1FRNHs`u!Idnd!(NZC5#)&-G0Ydkp^RC8B5GA9ialN=Db\9!^V$8$Id-&Tn;iE2^X;P@#6+-RZ#s4aG
]:Ba)Uaq"MD]+5;q+1%<K#o+'G5KtVOj9tg.:eURU_Eg9#>i5dN[CuU\('%R-N]f\:1SkVN5KIg*-I"<*^0CY9NJ#JH_rq4V;WP6WMO\G`H0E7jg6!"G
eHU4>g4@XP+q5?B[a<Ksm!U<V&n"gK]d<h5m?t134nWFqB*!]GqaAY(]^bC?+H]%7fgs[<5C.&i+7pbp-O@9Ye>lA*+(BJjUc=L*jY_2(S4(a*om]&P>
KTql!=R+"Y/_SY5,@j#N]1&ik&<>c'B[@^n)IV>H,-j<d$u#:PT'Q62laaaDmT@CVPIKl$bjV+ZKb9g1b6O9'Z5HrrBNfIpce0,FY6$H;dYs[YmL-Ju0
t36W5i+SkT)!9@=_+6e&G@_H0eH#$hb^PBlFITPi;GWV#F?q)BL:_a[bV^LCo<!Eg&!M_Q?O+n%e";2(;egFBs0<j5448AZ/1;Ep0uL*O1]<JAPD\Gb@
%mH%>3:D6Rhb9eih<cNl1:[JGLF4QnJWijX)h86E9$)>Bfk[1uSp,0+/sV0'-Sq$gf]5^SG.k5/]k2(5b9=OW>0A>ng2]N\#=t:D.ohQ(;eZB2IG.:TG
LdKe@M8pU;[;O(ZKNN>)`T0K2g;dr8KnK014`1JIFiCbV-@7fA7=811Ks'!-fiJnnfE`\ts9+2[)`P>9`'!:O[R9NBCh8IO)/@XK^-8D,;i$VL?g:-QJ
Fs2B)OWSg.:Rci/qkZ;.R(^Jl/-+f"KRK2SGqc,B"lOnE-Uf5O(/<Kp#Uc6J/OZhI@hNe!ZZLr>qP(mr33Qf`j9d^Wd?2>]r'RLQrouD`e2=>Wl`Hn%*
CSqdNQTub!"Q3%h74O1=_J8j*9+DPDJ"h*SDLhP'!E^(@JlE5XN04E*MS@@5M6_#8gp&*_d"->OJKonR+I`o-Lh9^=Sc?GjSr.agUZ%<&RK8P\ljHQn6
afLOheqR.=<Eq>G(=_ZLZlR9=3GM#Ku>'d/Wh@kE=.<9;$JTWZi,b8-?M06?C^`$_(TNn9<6Gu*`4HW_K2^m$h/<>5[]a"GY#L0djt!IK*C6a5Z-!?>t
JYn<K;iu0-"K9S=h]rN0d%+gt5dBCK(i^.3BtX,8<mAQ!c^iiq4+ceE6H;TE5[j/:o(^;"=_um?Se`DGP>9RVK*djZ$tl\g/I\SOiH^C"I+B^lh&Y\a-
`]0S*_Y]4LNbA%(@r72o6ro)IgOA/Tcd&)Pqh%A[sR[fEGGn85j)[T<r)ru3R.MuZ7i;u3RR,>GR;L?Gc#n6oMTGmGM>_^Ko"SXecmC);qu"p^O2GkD(
mG5`gdbmRK@*/HU**9N!N8Y9l,"D[;1)"B1J#KsuS\(aW*#:#B?XD`^Rb9kY*`"-9d$E0Fk@Z;JI)\-+8QYWR,b!m@q:o[XT!]Z.uHe:0+2luSF"ds5*
\A[CV=6Qpt(gV12*66(:]3;>`le^IUH.]Z5E#"0lNe:f(5!r=82Z'Q&^E6/I>BkT#7JJI7L8_T[45.?APZJ"V+f'H3]!`Jj?d-B&B->jV:'>Yq'/&Yuq
V:l_N6l6EE_Jc&&c$Zs2B#mnoQ'YZ/#Va^XdsZI8"Du@eQA<Nk#+nLm2jr?L`!.Y:Oh"uZ**DOe,&W2FSV@n,?N^62]BMPTDTrF?ldDgY%0q)&u6Q!$m
"b?It)KZ$*,OiP?34I3!5Dm(L:R>N>,-\A:#,X(JM`Pk*(g7ISq>YVV\B&1iIOQR$"YU?a4^,6)+Cd1[IgOA5]u)/Rn\(1F#[A)<KC<e)"OReobTlc/I
(LZQB]b*rdeAC03SthnspnY4M[t]2krV1F]l)\7N4=W0QeYFYBOQM8WCI7Y5c3^0HW:\e>%Ckl),!"s[noiSONZr+4]4DksC;S]?dtG9/t5gAg+k;kH8
Qo;@ZLo',2LIerhXT0E8Me&Qt<o^OT,55p>kl9%,a5<Qm$fTY#XpYB3XB:1l(lGooj-J@h4(SAn3Fj:1)A:>@hm;+u-o?M':2CH5(BCS>R8`Re:E[Y:@
e,X7kXZV$n3+[]*j>!"N5@4l^4`ji&Im<AHSX2M5r*\s_"+&rpE3$e4P$XX(<H-3=XL;p)Ioql=$Xj^B@n(?L\GbAi?.[P/A%5F2q&MBYoc;f!];4X0;
WCUgXhG(LS%tlH5_KhrA<4`tY\b:;bMU`GPha_`d:Y#kh%I^jB37i8PDrDORQT@a=1i/nUS=t1n80uB>B\)s!b]lhBV7&=5#tl0bVX-%FWG=*bS:.:cS
@F?,j,@P_$qXenE5h&NOq:b9gae_hj.mbq)4"Lesq?2UJ#/E3!:Su)JmjP*LTGrgD+]&+RHRsLZ,0<.tW4^IV-d?jI7j<Mh5#V>-=5Lg,kfT>^oHc&)a
T[@omg&Nf9RebD66&*A&)]0U6!GR8d)+gD*M*:'$_/D=0gr@/3*(A1DDH0Vpg,3'eT((kW&rj"">#"oI+qD`R5`OK;V;E04Um["Xp2%.BC%)c;Iq<f.5
q:%e13V);E=W2dh'9[g(<\'ZjX=n#aO?[>MuV;`-?234>'&"IGADg<!\+IK6@_7Bc4s*QkU\"(#!?lX8.U+]sjD/'(pACMFTrFD=12[6n%<-D?"cES*.
Cn(>PMWQt7Ff-?\)+mAUpn2.I3!l?HM:EMTaj"'hl2h@&N*a7gcqi!Cm6`!L*L_Y?1)o]2SZ;!3CZr]O&YUL+;N:H')l*%*Di)kV4*KtnoF\lZ7]OZ2S
FGi14Y7j&Vl2)Ua9D7UQcNdjpZ-O?,'$Q<ANXr"jXH_m$ucKoh,U5aGG!@Z%3/-U,JD4Z%p0t.+ld#acfpjtm1"1h33Ehf@>P<''0MqT"Z>YS-;$hj:k
9[D4*8n;#oG>kkQa6Pp35Jf)Z8EB6RX!46TC@>hHcX'AqOHoIX(DLc)ZJhIqlG^L[BlE_q+'^p]H0YTT/VZ'1DL^BA>WR!mIg49'`a.Vp\&9/l]CuX#$
$tMq(.jpL?'Zl'K1Q<;KUrIT>XaZ+<it2_2!PK4sdJ'3jnC*RkU%\0oWcj9G.)Yg>_K^26`Fb.^GU^0Oo]$qLcTV&]s8aSD7D.^Dl@3u>VPa!.2r+.5B
c\4W=;n0CB#_Mj`o#S0?7(A!78C-_VO$61Q&BqWDGWJ.Il&LJ@Ec>%?l)RV5NB;<KS8I9n)pW;LL'R^`A6q8i6^1AARSDL(u*6rA=B;\Tca&YrNe9?*(
YrCY+GQ@?0`J9D7E><sX64L@.A1aR2nci+Le^^B7K"JAL&.eNumTjXeHl_FV>?,08>)es%AoV\a5P;m(Q`G:8g/#baF5R(B,@N[m`NY8&Y0onMo8_']L
8jjG-'.B',+58!FhGMkEO%gZ,@S[aZ1?HN9b#kO;0B4"*,G2S*>$(>0,K$"Y?jI"cCq<$,c`lg[p^0I'_][=Wd]ISr*HC0^n5tQH3SleVs4`hq(bsRi6
PK(3e0G%Vs7pio1c66)QB"pE/h@ja9XUe^=%.fgD%`71d6,o<-(ALVd*R_R%%Dd.TjMA9*K'Qm=K%Hg2Q72c4GU-R=`![:lQfB_Ec7#pcJuT0>tI6ha0
F5nLMPY&>'FbO!:2EM(Le5;O8_651INa^6B;&8O+f/_4tu>n[>mknaYOAO5e]li*2<e44uIlM"?6p'''
	exec(zlib.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.63'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-11-16'

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
LSBLK_LACKS = "FSTYPE of an unmounted filesystem is blank (-F keeps it), and UUID, MODEL and SERIAL come from sysfs and /dev/disk instead and may be incomplete"
LSBLK_MISSING_NOTE = f"lsblk not found (it comes with util-linux): {LSBLK_LACKS}."
# multiCMD's return code for a command it stopped at --timeout.
TIMEOUT_RETURNCODE = 124
# What is missing when --timeout stopped one of the commands statblk reads (see cut_note).
CUT_WHAT = {
	'diskutil': "an unmounted device may have no SIZE or FSTYPE, and UUID, LABEL, MODEL, SERIAL and DISCARD may be blank or N/A",
	'mount': "mounted filesystems may be missing, or listed with no MOUNTPOINT or FSUSE%",
	'lsblk': LSBLK_LACKS,
}
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
	"""Byte count from a diskutil size line, or None when it gives none.

	>>> parse_bytes_from_diskutil_size('500.3 GB (500277792768 Bytes) (exactly 977105064 512-Byte-Units)')
	500277792768
	>>> parse_bytes_from_diskutil_size('0 B (0 Bytes) (exactly 0 512-Byte-Units)')
	0
	>>> parse_bytes_from_diskutil_size('') is None, parse_bytes_from_diskutil_size('no bytes here') is None
	(True, True)
	"""
	match = re.search(r"\((\d+)\s+Bytes\)", value or "")
	return int(match.group(1)) if match else None

def get_macos_diskutil_info(timeout=0, cut=None):
	"""
	Build map: /dev/diskXsY -> info from `diskutil info -all`.
	Only used on macOS. timeout: seconds without output before diskutil is stopped (0: no limit).
	cut: a list that gets 'diskutil' when the timeout stopped it (what it printed before is still read).
	"""
	if not IS_DARWIN or not DISKUTIL_PATH:
		return {}
	info_map = {}
	task = multiCMD.run_command(f"{DISKUTIL_PATH} info -all", timeout=timeout, quiet=True, return_object=True)
	if task.returncode == TIMEOUT_RETURNCODE and cut is not None:
		cut.append('diskutil')
	# Blank lines split one device's sections and lines of stars split devices: a device ends where the next one's
	# Device Node starts. "Not applicable (no file system)" and the like are no value.
	devices = []
	for line in task.stdout:
		if ":" not in line:
			continue
		key, value = (part.strip() for part in line.split(":", 1))
		if key == "Device Node":
			devices.append({})
		if devices and not value.startswith("Not applicable"):
			devices[-1][key] = value
	for current in devices:
		devnode = current.get("Device Node")
		if not devnode:
			continue
		# None: diskutil gave this device no size (0 is a size it gave). Disk Size first; older macOS gave some volumes
		# their size only as Volume Total Space.
		size_bytes = None
		for size_key in ("Disk Size", "Volume Total Space"):
			value = parse_bytes_from_diskutil_size(current.get(size_key))
			if not size_bytes and value is not None:
				size_bytes = value
		model = current.get("Device / Media Name") or current.get("Media Name") or ""
		serial = current.get("Serial Number") or ""
		fstype = current.get("File System Personality") or ""
		label = current.get("Volume Name") or ""
		uuid = (
			current.get("Volume UUID")
			or current.get("Disk / Partition UUID")
			or current.get("APFS Volume Disk (Role)")
			or ""
		)
		solid_state = (current.get("Solid State") or "").lower()
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
	return info_map

# mountpoint -> the done lock of a thread still blocked in os.statvfs from an earlier call (held until it returns).
_HUNG_STATVFS = {}
# Floor on the statvfs wait, so healthy mounts still get answered after a stuck
# smartctl has used up the refresh deadline. Measured 2026-11-14 in Docker on a 32-core
# host at load 210 to 226: 120,000 healthy statvfs calls through _statvfs_with_timeout
# (thread start and wait included; /, tmpfs, /proc; Python 3.6, 3.11, 3.14) took
# p99.9 11 to 14 ms and at most 119 ms, so 0.5 s leaves 4x room over the slowest. Each
# mount first found hung after the deadline adds this much to that refresh (one already
# known to hang adds nothing). Network mounts add their round trip (not measured here).
STATVFS_MIN_WAIT = 0.5

def _statvfs_with_timeout(mountpoint, timeout):
	"""os.statvfs that gives up after `timeout` seconds (dead NFS/CIFS server).

	Returns None on timeout. The blocked thread can't be cancelled, so it is
	remembered and later calls for that mountpoint return None right away
	instead of piling up another stuck thread every watch refresh.

	The thread is started by one C call, _thread.start_new_thread, and waited for on a bare lock it releases, so
	the main thread takes no lock of threading's: a Ctrl-C that lands in threading.Thread.start() can leave its
	_active_limbo_lock held, and on Python 3.6 the exit then waits for it for good (multiCMD 1.60's fix).
	"""
	hung = _HUNG_STATVFS.get(mountpoint)
	if hung is not None:
		if hung.locked():
			return None
		del _HUNG_STATVFS[mountpoint]
	result = {}
	done = _thread.allocate_lock()
	done.acquire()
	def run():
		try:
			result['st'] = os.statvfs(mountpoint)
		except Exception as e:
			result['error'] = e
		finally:
			done.release()
	_thread.start_new_thread(run, ())
	if not done.acquire(True, timeout):
		_HUNG_STATVFS[mountpoint] = done
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

def parseMount(timeout=0, cut=None):
	"""Map device -> [MountEntry]. timeout: seconds macOS's `mount` may go without output (0: no limit).
	cut: a list that gets 'mount' when the timeout stopped it."""
	mount_table = defaultdict(list)
	def add(parsed):
		# Skip autofs triggers: stat-ing them mounts the target (df skips them
		# too); the real filesystem shows up as its own entry once mounted.
		if parsed and parsed[1].FSTYPE != 'autofs':
			device_name, entry = parsed
			mount_table[device_name].append(entry)
	if IS_DARWIN:
		task = multiCMD.run_command('mount', timeout=timeout, quiet=True, return_object=True)
		if task.returncode == TIMEOUT_RETURNCODE and cut is not None:
			cut.append('mount')
		for line in task.stdout:
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
					debug=False,cut=None):
	"""Rows of the table, header first. cut: a list that gets the name of each command whose answer the timeout
	cut short ('diskutil', 'mount', 'lsblk'; see CUT_WHAT).

	A filter drops a row only on a value that was read: a SIZE diskutil did not give is not a zero size, a blank
	FSTYPE whose source did not answer in full is not "no filesystem", and macOS throughput, which is never read, is
	not idle. Such a row stays, its cell blank."""
	global _DEBUG_MODE
	if debug:
		_DEBUG_MODE = True
	# None (the default for library callers) means no limit, as 0 does; multiCMD takes only a number.
	timeout = timeout or 0
	if cut is None:
		cut = []
	if tptDict is None:
		tptDict = {}
	# macOS has no per-device throughput (READ and WRITE show 0), so -A drops nothing there.
	active_only = active_only and not IS_DARWIN
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
		macos_info = get_macos_diskutil_info(timeout=timeout, cut=cut)
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
	mount_table = parseMount(timeout, cut=cut)
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
	# Whether a blank FSTYPE of an unmounted device was read (its source answered in full), so -F may drop it.
	fstype_answered = IS_DARWIN and 'diskutil' not in cut and 'mount' not in cut
	if (not IS_DARWIN) and LSBLK_FIELDS.intersection(collect_fields):
		lsblk_result.thread.join(_remaining(deadline))
		if lsblk_result.returncode == 0:
			fstype_answered = True
			populate_lsblk_dicts(lsblk_result.stdout, collect_fields, uuid_dict, fstype_dict, label_dict, size_dict,
								model_dict=model_dict, serial_dict=serial_dict)
		elif LSBLK_NOTE_FIELDS.intersection(collect_fields) and (
				lsblk_result.returncode == TIMEOUT_RETURNCODE or lsblk_result.thread.is_alive()):
			# stopped at --timeout, or still running when the refresh's deadline came
			cut.append('lsblk')
	if IS_DARWIN:
		for devname, info in macos_info.items():
			if 'UUID' in output_fields_set and info.get('UUID'):
				uuid_dict[devname] = info['UUID']
			if 'FSTYPE' in collect_fields and info.get('FSTYPE'):
				fstype_dict[devname] = info['FSTYPE']
			if 'LABEL' in output_fields_set and info.get('LABEL'):
				label_dict[devname] = info['LABEL']
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
			fstype_read = fstype_answered and (not IS_DARWIN or device_name in macos_info)
			if not keep_fstype(device_name, device_properties['FSTYPE'], formated_only and fstype_read, show_squashfs):
				continue
			if IS_DARWIN:
				# None: diskutil did not run, was stopped before this device, or gave it no size.
				size_bytes = macos_info.get(device_name, {}).get('SIZE_BYTES')
			else:
				size_bytes = size_dict.get(device_name)
				if size_bytes is None:
					size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			device_properties['SIZE'] = '' if size_bytes is None else format_size(size_bytes, print_bytes, use_1024)
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

def cut_note(command, timeout):
	"""The stderr line for a command --timeout stopped before it finished (see CUT_WHAT).

	>>> cut_note('mount', 0.5)
	'mount was stopped by -t 0.5 before it finished: mounted filesystems may be missing, or listed with no MOUNTPOINT or FSUSE%. A larger -t gives it longer.'
	"""
	return f"{command} was stopped by -t {timeout:g} before it finished: {CUT_WHAT[command]}. A larger -t gives it longer."

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
	parser.add_argument('--check', help="Health check: print rows with a problem (SMART failing, FSUSE%% >= --max_use, hung mount; exit 1), else print nothing (no rows, with -j or -J) and exit 0. Unknown, with no problem found, is exit 3: SMART unreadable (rows printed), or a command --timeout stopped that can hide what is checked (named on stderr)", action="store_true")
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
	told = set()  # the commands whose cut note was printed
	# --check: the checked columns a command --timeout stopped can hide. A filter drops a row only on a value that was
	# read (get_drives_info), so a stopped command hides a check only where its answer is the check's input: mount lists
	# the mounted filesystems (their FSUSE%, and with -M the rows), and a pattern (not -D) matches any cell it fills.
	patterns = bool(args.filter_patterns) and not args.match_devname_only
	def cut_hides(command):
		if patterns or (command == 'mount' and args.mounted_only):
			return set(CHECK_FIELDS)
		return {'FSUSE%'} if command == 'mount' else set()
	try:
		while True:
			cut = []
			results = get_drives_info(print_bytes = args.bytes or args.json_objects, use_1024 = not args.si, 
								mounted_only=args.mounted_only, best_only=args.best_only, 
								formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
								show_squashfs=args.show_squashfs,
								pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,
								output=args.output,exclude=args.exclude,
								filter_patterns=args.filter_patterns,invert_match=args.invert_match,match_devname_only=args.match_devname_only,
								timeout=args.timeout,debug=args.debug,cut=cut,
								)
			if args.check:
				read = results[0] if results else ()
				results, check_status = check_rows(results, args.max_use)
				if check_status == CHECK_OK:
					# A cut that can hide what --check reads makes the run unknown; any other cut stays quiet.
					if any(cut_hides(command).intersection(read) for command in cut):
						check_status = CHECK_UNKNOWN
					else:
						cut = []
			# Only say why lsblk's columns may be incomplete when the output has rows and shows one of them.
			note_due = bool(lsblk_note and sys.stderr is not None and len(results) > 1 and LSBLK_NOTE_FIELDS.intersection(results[0]))
			if args.json_objects:
				import json
				# Watch mode streams NDJSON: one compact document per refresh.
				print(json.dumps(rows_to_objects(results), indent=None if print_period > 0 else 1),flush=True)
			elif args.json:
				import json
				print(json.dumps(results, indent=None if print_period > 0 else 1),flush=True)
			elif not args.check or len(results) > 1:
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
			if sys.stderr is not None:
				for command in cut:
					if command not in told:
						print(cut_note(command, args.timeout), file=sys.stderr, flush=True)
						if not redraw:
							told.add(command)  # once per run, unless the next redraw wipes it
			if print_period <= 0:
				break
			time.sleep(print_period)
			# Devices named by filter patterns stay on screen even while idle.
			if not args.filter_patterns:
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