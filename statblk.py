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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 70):
		raise ImportError('multiCMD too old')
except Exception:
	import sys,types,base64,zlib   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
GhUEUl[%=,Z5EGmI"h.sUU=_8&4)bLkI*[oZTYa/7N's$/:62$#,+Ra6;.tr"DM"3UO5'LaiSg[ofI)4?JrIaeruW8oaLmMH"N6+\VNMG0@eV'e^`4#<
PSFtiMKjC4NeNOZc*/fH+gp?(6;Ypjg&!j]l\\-b/VnD]K0D[=(N/,f@e2l*DMFe4I`GD@Stk*h=9/Db#YQ3&`rN>3a8_E@U;Njj7Pi?PgLt=ap^'rji
'@Z#_+f!HleRKq-jaslS3chYO]YX<,U!IX(%6WAQ3!&&VGWVf(ikmX]OOSFuGr)Dp;>%V70\rRC+Cr05&62)JjiC<[@a2q#0X44hm8ZP)uPt4LLb$^O1
>!2LYSsm:"uroFAV#o_Y238!nS0=Y-4/5sUj&ffBB^I?lPWnfjRg%sI]Ffj?ZUB)=O-8$C@-:]Hsaq"3)I$1smk)UB5+ic4H9qWI(3YZQ2$:W)tT-qW?
D^DHR9U@6r$IJ2.Kg[ra_P#^)('UR!jSd#,XkqEtR]@56VW#``^+*'PnnJW<mpG-.cG,P.]^+S122D-A&T$FZ"N(GIde"c)U8o>tqmK(=Z4IUs!_TN^a
bA7@"*9\<YgK+1=e`"WVVlpW'VpCB1*5AMj'7B]PZW$WHMuf0,GL)?!f2(<'R.0loY:fCf7GsN%B`Xj`SK+Mo-2E!P0=+]*FHX@%4urI<;O$"VpbGJTI
p&$37i6q%T>J&ra3P5k:=:6@*5?i+6feuu<?M'eq!&CS+.g2<r:K*_(N5A+]mNRH:s3W(RNDImn6*&pL]gq<;FPl_jXF0;neN:>+Ri0eIX$;5qTt;mkt
g3/r5B3,e&CQ4T6V75EkG_^!`a=S`q%dDTAVh9=)t6_\klW-r;.;hl%7XX!`:Pqo4`_bIC^7ompN/D3*fc75gdDmGVF^[B*i3@JdX3*4sU.SMdl(E`V_
%$=W-iB^=6.Yk!b[A(S(.L8^@59?hH^9"-<l6(4\oYhM.XK2T/*M]W1\Qc/6m_e$VePnjL=GbAm@7/dbSNh2C<+5=O-!6E"=UN/*H`Vi))-X(%2g2o`c
7kd/4rE(AK[C\g2"In6I4A0#X0JW&Wj@PL!G&AmU/s7:Wf/XLOoe<us(J4Cl40?5eSN>Lb\^c:eD_N;?jI@OikFmr=QICNGqX6:)Sq'MlW:g1j>/([^-
H/5M9n@QKNgs"A1Zl)653'CZlAY-\ZR/rYk-9kk.ShBre-fG%UOKnZig72b2mpe'#eFp`%9+UnQj.(PA-6IhB"K7/I"J_6RW=RA]WTm_gKt(;tlcj2'$
0;2I_FOAq08jQ<qd.\M\d/6\#s@06cU,G;8\P.%)pR?jKc1=!fmi3167;<D@)<I%m`9Wr^UsutHQPSM72Qd#)EsEiafqD?&ReV,Q[A+"[Tit>1>:Coes
*DPLUA_ig6V5R!hBZ0\PV`'=;3m#1Vc5N"$6q.#e1Igj;]"B<_gZXbR[(7%6sR:n4o1H#Hdl/TAO;'Zou5@VpLiGH'PRaXZc;DDKjfhkOsS8jqd[\?c3
M9XEk]4ILiZr.b<JnS&LVS$u\q6k:9Y4MUf*WHT<]O\"G*Yif-SaMc\"-i?WNI`]:h$n$U;jK1HIO.cZ19_GP'J'J$63G5rqA/G*I2-9)sTp\7%s#?dC
IJ4qm)Xb:-;8$WY*`Bs<+@qBqR07YAcP:XeL)VfpPSg/Tao^1BtVnacg4ah=5g_eW4p?g8.aF6:$GDkf_XY9f)XlMG_9$#s8/O@5cV,Fp_m1CqY'FRR6
*8[mg3'Y:X\@el4]/-nDH2\s[;;`me)d$sT0Sh-*d*$4gllVk6H$/meXdFo(r5u4,3DbM*(939s%rg*tYVPA,1^u_$RXo^,Gr]2)_\h:Bns7AcJ.d,[j
-66tEZtp=YurHlOa`"8e?@X<-[W+/JCOI@[8'S&ZSK@mW@"GArAoXuQI)"a%!'pDT)UC3g6JPYosOBd[,n1+JtZL8_M"j7icIe*+M.fNUl<oY<2ZV<K"
<o]BrlpQ,ZkN9lTCY44VU,5^_^h`OcABT$@IJ/q.:9/1ZMS$nV\Y[a%S8$KV<u!=eLL9\F=<QD\!-s:r@W)6?(i_F;qWhTt[K+o[sScbG_o*$3W3bNat
udN\Jn*+G1V-&Q!*GYUS4U)cT+)p!=%@?_jTFR>u8j\CiIn6`,o"&2AXtT)Gdl91*Rr!Y]>U>EN^(Ge*qG(?@ub\Fnb\n;%Frl3.>[FIR=DHHbkD@2gn
cX&Gumk3+TB#Nh/(`,,L7Y]8C"@5q]Q;lk]M&>7fGr0#:qEZNM:38e'5N4["G6Kf,[]5&W;%HdI1/!Jq.:EV.#fbeu%e-g.D[G6)Ibe'QH[pcoSF5[/&
a7p75A<R\CH[tc9ZTZVRXsQsPdOk=,*I0U.?T5qb98+JpIRBZQ"69WBbn3jTOg9[C5P,7H`gGITr7LVqpo^%iiH_te0aR7P$^;SIpE8g;eA=97GQ1$m0
.9I"[)O>SrWok+Fgem*f8ZP&As_Q>7Bt!gNU$7+5H/*7j(1(t`tt<*UT&GZef<Da<9j_#c*K,qnDV0KZkU$rOTZU'Q"jq&n[ZQ\Y/]q:6uSg308dkuc2
7!7G<G]e#)!JW.*YP-"]Ee](XDkf`3qX`q6!8Ri-;lfA:mONN8j1gJ67G&;GT=/&FP7FOthd=JU_k17p$r<g;Vt%JlEtL)nd0QCRHn2d0a#E#_XZ!Q7.
p;+6NahW6>N<ls:IC8W#r#$,X.3JdPoC3mWW&khZl=K.+9(\pY1oV%'n/J2uie,PA<?D*nmk<qJB93Pr0"<$*&IA;!Cg/bi/T#W&p;PIF?F]EQF9k\\a
d&Z%0Kaqs;22TLXtb+0us*AIX]]V/kH8EDGp;^s7#THt28^4V.t+(M:4lVS<-B-FD<oBR6_l*Be)<6TIie],$P`"bgAW/8B6S+r`eF`!Fcf#01lJ"l0e
K0^W3'KW-qn.38XL^?d.4V="U'GV9X&NhM:@r0f`LT#hZ?^acA#6_8f2BBC4GttXFTTh`<,(Z?O`)3n],N=h`0L`lVK^oD.&Usj2HB"9r^(Db9GaoT'P
u?KCeY/$hb[@g3K+IkIE'V</ZO1,T)X(9oPcK[9!K6#p_J(O;pu)uthOO)YYU>UaC1FBbfJA3or.#M2$IWE0A9=0.^qJ#a)P@]k-0XSe(#bZ@_?5d@IC
O"-B]_$qVF("&m#n;@;D$GW0[dkBk#%iY1-M@oORH4;o5(kdNGRQWj,ZKE2q()cGBB</eOutTTB^5(;kq(?)"[;+adNaQJL5r0=q<kbS/:KH9bTbQg$;
.WMK9S_Z$5smaM^Ta[!t$<;!_(X7H2@+<kb[E5aqRL[]jU$#.!T4((igo[UGABlHG.*Ccke#Xp+^"DnjE,dBhk_hP>-`RQ>9ki[r*nMqWDq/KGF_4>oJ
\WpC?6nl/61[2hSM0:NKB[?t-b>\'&m$DRF+Jf(hY)T%;AaeOkG3,gT+gBqDOD`/!i,]=Cpa`rBE+[T1MB,S&ce!CEA$)-P2o=S>Ra4EBU`&S*R>NEV#
2I2<G`b4neQ6=4!MDH#MUuST=4L_YZf%J`^6\;YH^)F1&(T^D@kZG%,KE>p,P<85"7JikuS^iDMQsosc6M]p$1Ro]"(=?B\4JKrl`pem;EUSG"_(Oi2p
+!0B;<gKMnDO]u?[^:Y*hU_Zr'@H=/nN9/<?h#(fW'UE!p%6A9enq4l:R=s`C$V>2W'`8el(;!N$Z;5(1g!u-@(I'dRB;$LsZEA(F,]oF:Shr+=Zj]JM
NFG9J84d)/CJ!_*I?+>akaA!o]ha*DJ6B]C@O%QW)e#@ns(XesQ?DYpZ>B"_"U77Q%]L8mhl2,[Yl12oMtm_TmUuYoX,1&XX3M@SboobZR=eUuqQSA%2
\!PR$b&N5I,r$k`FS7P[Br/70hUN_o88U?4D*LusOJZ<UtIr*r.d"7md;)/^W@X/@<c%FYs\Pb_EUh/n`7jZBAY";02._jVi6@^ut>L'a>P)cQ,r!;B8
jI[ab]'5VNe\.,(anEj`cD"s2i-UNLM1rmM9lQE!SnX0rV/h47][a`Hq>N$ebb*pt>ZW!,D@PNF;<>qRSX=VET(9aYGfI)Zs*4:.-VFLk:VG-48i2i;P
-Uqt2FIL\jciTd&YWN(/)J?aR,bVS-F?5/9[^"+9IJbpfX1-dJH"LT>9",^SCo(':',%]4"L<DY>X?X&$5Xk''7@8=hIhbuq3$"uoW2.Gpt5I<"qWM]B
jODO7N3@1Ot>/*B*:dm5Ma5P=+>JkK"`.4"9Dr!.7gM=Z;jnV$ZP=t#rM8PdJ(\+6o:Y`0!g4QnJGq:"JJ$Odeh\T.5:MoCpTGAh0%T)9&CUPI=Cr<rO
;6'F0-5`[VYG?+2<&?pu[PXotm>j^A[ip21FR\d;gX@$O$9]06PL?$8.84gfKu&3[tgOk1,_)Fg2@VlBDJeELrM4)!2$]7!='e_MQDiPY<7b?T5LtU`q
;LjV8e*4U8+C1qY;t)Q7@i)g9ZO*BRt98d9!oI=To^)6)?rUS8R)7?[9@hX5Pl!B"jf\FNK/A?d[g3N7=#$;F4g6qOD=&b+UFUBkX2bNm..n7+B0XG^)
RiWHW#g=W3>1m(A=gXW$@07lePjq?'`FcF!<=g,na8"NB+ZHlN3EADg-'_?oP>U+[8&uefna?;qJXQ'u#3O,9bSs?B"5f77;fWj[o);#Uf(0JOC<IKM:
eS&noF"AX4OC(aneBhRUjU$P"QP164oN+el#[-e$E\PN.8*!sm)uZ$aJ3E[W!6AWV-*hrLKE)ZOG5U8g.(?#*-0?Ok<+P/ifS7'(d>qZ[='Pd8LAe*J^
J\Qnqen=KEjjke!!"XTQ"9=n,8F')DF$=ATl33)2n,JIO:8b:WnmjNTN8WERgYnfCm-a09Z_LKB/jDonYW*4d^ltHkC[<#eS'H_FC6IP1aa>X%QJVRX#
[N8-;6G[Z;PQb6g!Y:9YJ>&YpXna'R(36(K9pbJIg4_VJg8XLNFm/)aiVHVC;>]VK5:@ik@.#IN.]9PUk@F3.f\TR^7$>UiN%A`OqWSe(hU$K/j_eNoU
[!961e6B3u-S#b>be$"c*t&ukD@f'&ZtCr]-Gld?Ft'h_M$"npgBBJIaqnt&ZrG-$!l1o(1Fj[+R*$R/QOe,Xm]0;:V%V,^P^>!'qg-U5RNWkF*UF3+)
"(5iCQBmRk8,J203EEB+DJ>o?5U9;cWHW*5;-(1WVn)J.6R30B%k5H5Trglbkf5^=Z9-,a2C9?Ne5dVsr1(gbUG/s3*S>D%!Jt^\l4D+7e3\Qa]f&Zl7
I3>:sB".4;-<4J8X6[Qqp1]NYMJX-iaYd.e'T7+Ji8+22BA=T]g-:uGP!L+h+C<JiGZRN4,@Mn(%Qe)-0>f@iFm"I:@6T0<9UdJ&LhL0H5,Fl,N@IFe)
FO2hr)f@p3)t###E=?M%hkmcgpu+0kR_t\L["r/4PieU],,&6bFN8b<P%!QT(WbOUM;[17/"gT&_CR">(Q1B79H-bU#pmjCqOkkG=jIOU"!_Y6hnqW!B
qt3O3c&AnHgnh^Eh4R2\ouoO[U*ZKUIJ-8:L33M34j&jW@fn%`fVjTN%gS[+?bPB)sQ/m4M@>;D(>-P2+hYZdNh'l)`rC?+3m!c:<\P>`9B'%Vkgh8>_
6UG"W<5S]\j%Tp?:e'gem7L@K&9NLYie/U83'7Z<RHf%6o3`Q4@T5X*O-*e)!m;$*D<ZU?grTa/o/r=hkK0JumAC`PgF`Vetf:@1]CqIma:Uh?0E5,C8
@#+@e/q)P`KB;-_)%21ur^t%ge&^ikj\tm``@u'!QjRje_S&6ck:95Li;-t>QWP3%80*Drd+3*o"3aVDj@UHp(A^]9OS'R8s!,LOj";Y5Xo+1C1d,2nY
$jUNYdM_!i5XmeR=?)og.8H'Udl&^BfY:a5S!I/W=&q_qG(2abi\VMWG:]U?nbRd9C$/>hfEEGAF=P_p&,!4Ng.Y`j>]$>q$6s?HVG=>^n+KLBI:pXo.
Vn)MM^_jX;Bf+?O_Kh-*+lAGhmo98=[cf#Zs$Pe$J[McA.Pe.Ze!!qCCY%lA5:h1fE)n5enWI<=!M`DD:]8iNDeF]^Lcf?\mu,T3u:7W)'[n8/T8r"p9
/=QZd1t/-$^n7USso#Lpj6H,"qYA<R_L2a/!k@dc$^V^*0d]%?Y<A5*<<hK8X?2WQ;sQrTpFYa2LW2HhT6o0HpK0)i5!O,[3'^c=aBC`76m<`]bN)k4:
jS)-IgrkF"KR/C$5ReQD.WQa$4+Lg.;eSpLUqYc7Ac:7RS@Z.1*=j&C?!LB9E%[/")^;V>`WN/83fBCiF[dkEfGQ;]34)cC%5d_=;d!rd5p&]Me*,TmL
gRNsbi3RO0me9`tU!/G)SJr$Wpg+^(lkR&;*&s_#$a@k'Q-*I-V>%Q,Z/=W^XG*8"uV(cj>QSB<.4FnNs@^Fj!,,$TeNO;.F@ZMb#iVa]iJ$SoJ,#!:=
?<V9m(/l=,\U%4XI1aJaf$.o7$`@$AT<57RRss!X*RTj@1#F@,VXCgN4O%24;2]$XjOTT0>\pZ=<`0$<Zh<D]CCf^sr@@.L=r-cKJ3&J8k0pTf3m6f-l
]pp[4I2"aI.2O;fP:akgQTl5SZR?5c+kjl8lN0rc=[mi`n6aI:DPW3KjO6*KU@?)Z,luUNH*dIqfHgE#>+IM@Lpd@4\ngE"dsIH!'d"#rI>_\NLR5qrJ
#1MKI9&.2K._nfbDn416ak*fdH9>"RAFVpp:'uD7/Oadg@/<du`'PD_GO,`%id9VK>e0_s6/rX%Ef=@1TZ[/I;>f62#</MEZQTO90n8=TJG.9JSbHB^`
DE),m]6h=tOO60[O+g9%QdFb4=DM<Z2Vj%b(<h;!$<ed?.m:K7V)\!Z;/E7@r=:7(b^D#Aq+X9PM+SiR3S!+iacZO*jAr%"lOPk:Ek?bAalj5u0B-5s$
2bAfW*%LFAipL2g-,WVM89lJ)Qo9'Rmo3%+)LbZ:s<*r-e%K64(5>km2`<$,p@E3hM[fm^?LWOS0()a_Gp$rBohsk^J`>i[pL"6V\fe3J$eMbk#dSos<
K<`_d.LVINAbV#T^Oo]C\3<B#35A]:ZbZm3WFbcDJ2=c2c3ATVa!AUHnMFZ9cNQ6?7ehe:+KG=Vg"oFEpMM,>mIYS*iQeP>`()B2m\>H2S&`2(`k!NO\
>a5?ktC?[HrOh$A0+XVUW?&Y$:iWY<C?OCT$N#q9io&)J!#0?$hcEDjU9dq+T1bAM+67BLh5"r#:6>UTQ*)$?B!8Y+YTf+Onh-ob*T!rBXYs+^%),UQ7
Pu?)m=Y]Dth+c\;pDmBlrAkGF`E?@0Th4ZYCLI3RDJmk&lnDOu`!8Rj!sM#D21B_PD3i@l9bu1PI'/@o-fG:GW2(2M]8*fOKrm/u=l,n<1%Ke4[<nL=]
VOll9qSPLQoib,!&nSX4/Y!7YSM06BKhR*sA*[AVRpb,TXZ:S<_MeYtC?6cqX3:JU'"Lf@"`76\i3'F`_K2eUbuB0BT:+<U=M^#Y"FpB/E%2LUSF!Y!K
8UJQTZL6B.('!X9oPUl0'RJ;rCefdW*>_k1j'L.6TTadQJr[QWED7bV#i=kohHOT-k=2f8;+cBs8'1fnZrhP)`>3UsC-Z@Hu*kuuLP4ZB+GQeU<ZghVB
5KZ0[e6k//5Mi\]\H;*<n>M#a"^R<W`u%W'`@E.00h"Np^1<&m.$IGVZ^u<Rn_(4R9H&jWD::7l5Zj6Q8'E!J'0Fnpo;bclOX[!OXAT:_7*&u%Q3H?P4
ut$(@9fd2X&H&Yd#G#fXTrMeRZ?LTY>VTr?*@[TYsS&h!=GXuHEBn]7-3*@RQJ(4/D_a:[cA^/++3bCQ]JkdO)UYjm:o.Q<Gg*C@rp_02Z0S1e;F(I?*
nN'=#ZUL=bE7lMl<`sPFS^m&P\^J.C@WoYA=C/:E:nV`0qa4L=o0J[U7N8-:(T,Eea:`]X8;u:pV^@;1`tqJ`_s'':(W/O(GQM>eiM`<.Yra65_3MH!@
+(:^UF(''\]d2=8==FX]u%<_Y]]%CT6\G"sffE\`sG\C(q-X`%#3<ZN;[O6S=.2!oCU<hM_bK27q__G+]=e`$+0r5`7sZ7FAI1!4KU@Z7(/#FIN%QlJ#
0Q-UuVN7+=t5[oQ1Ib[<X9CK.^p/l`N%?GhaF([4UgoHA[Z[1ri^>Uk?>'cPa'iTW8HEM[H7MR",E(,`DTh?B#g3E//<f!DLW\uo\!o>!W.Ml!nR]CN1
O4[:Pe6m)&ReRm9!8;#YAHCZ@A%*W3#KussmlM(NA62$UHTKXcdjg33P]\.i<u8(@Z0[7TE7;-nIX\PV7A>H$lB/+$8ierqkmNt-3ES`5d@"%3UB@`<q
,`Z*\d/95chjdArI]:fbAY,O5GtE.s,6h3GQJ^`M.uq1PQ"Xu5PXfm_7>d)%AfUuBq/R=WWPQhTp6ke`TMbpo!/t>SSYnY$m-O(*?GuQoUeaH:Y]u13>
p/L`(bVm*X;gMZJ)4(dCK1HnZV;`:%lU[OL.O=#+Y=3"1XTroL.,((o`2[C4\:EmePCPfDkuSimC2dFF+Tj>G?[Ac$n\<9PtrRP@._(060=TReokYmI`
Ypcrl(M\U$FMUGMRj(=lZ](WkB)7f\.t"KBb4<M=`4)V#5DKVD4q,'5dXX?qOP:-#MS!'DhFK_V3B*@PEIcf`:#Gj["FB*3G2DUGh6Zmld%0%%&W+J3?
Q1.<)Vn=4@dW?9C*QY4ceg^hdh\lU=4PbVG=T:(88`mMMh6]Th*TG_n_LCXb^l8HolS`W2'Y*Yb6$JbW4T\f'ZrGYSI>4/#V_;q)%#3D`I\l'C>=;lr_
O="%=hWu`ki*Hp:bOM%i2u:H^K]G6$%@_='UMog?A,C%,ene@a/V=4(=<ec$"0\8#J-<;1d2!O`([Ht^0+1mbWLD%EffbUFVip#Dgea+D.f+;C:n`Lk&
VhJ^^6[GM5XElr'YW<sPm'U0@.C@aUo/)Hk%K!QjqI4>;*;Y<Enpor+SG?G$GR%Lj9Vc9:U"Y#Re?m&o32sO98"T6BXNsR(61(?cOnU`dtn+#E]Lj;"R
)m=P"Ter=1+%-U$!*N;^YJpBU^QoQ.HqU%V7aLO(hK8QGM7!PpJ&^5VE,:Se=W*,+:Mi#u_9IAEg],mkqBVL]*?^+1(B+9/[3^NXoL1N=ZBW:s8hL=t$
j&Os;U_WhPPc[&2jYEXR1NAi3?F\(R9`g]#4nZunHPnD2J&JcTLZ2nA[GNm^?YD5(.GO4`CYN9h*Ko]N0V&8f/`bBg_l"jAY#8)Qm]HEm3il$m#J$rIc
q4BZMcQgrmuZ0UZ;(W*1H+7@(1C">`f*k6#eiY2d"0WC2qJ7^'AW8-dDRAe5.Q9olHM4)>ZoN%85[$1KmU.'_."<70eZrnKEfH%cbQ;kgl`F`Ze67j^3
;+6,T^+`Stb#b8d<WAq$`<&i(WR7]P=%QHG"[hRWL8S&cESn5V/J]/l=FA1jk2P5I\tV'?h?WZ3MH$6BgT/B:!D%E99)l,I'c/Z%2p219:q/.'84nG,0
eRCO^R7fU5R5h\bKBse:pb!i5bqR`40hDn-f9gBbjYGVrr2dFnt\Ok;9MYYb=)k/Y$ef-@m!1?X$%NNb,,eAFS:;n@'L(EgrduF'>kn<lcg'.AH'B=L]
3*9,Jpl=*K_BYVJ'EY-?igd:?t(Pe/F75,5_PaVc*je"j8GP*RkZl<\_`49/<=NG2rs_aN4l9_foDnf)>pdlY]S/']S*$k]'Pt,;[JW[5S0/*SdYl0X2
H2IGQ9K0J\h2o[&pXr7F@4o><f*HM?DfUjW$Xb#a*Qo8<b\])RKX]=0BH&3"L"!b7!Y.XVDsK.g6KI"m78`E^>\;Nk_]or2Au"njW*5tF`3bR^_Z/tJI
A0LA[;!J'FVL86<pP@Z<so&rA=R5"6JOQfAta!,Vb=$.nD&)6<U[r&%j@8cSYqS:[Z+1a^TQXp_goV=fiO4ZU7=t[h<ntK5j!rlEj-=5mO<E;D:h5p0)
NR"qa*&`R_>pI@mr9RP#8q00tL"Kld`^b?<%fOG!8;7i[`pXoCnE0rS9`3!*A0"NI,a"/AAC#reKP%="P-(=nl?Mg:qe3rO7O(JqC!@i=)CagtPl.4ih
p.O'B6!8HI6L#&-02)7gXZX5Chjt+AQ)pi-+&j)<L[u<XZt]&Kl/.-HHe!f4,d.&@?C6#_KfRpeu#HC%c>!JHLb"1i3bQ%4gR(&3S-nkjT`B.fW?p9[T
[ZQmVQ3qN7qQR<Obj\V01@)p07I_/&NG!mbajua^Hm].AW.YGd-mU+s)P'XQAa[)CP4O/pEF0F4OrAg"g-ID=".g/*=^bS<B>3?54tup-ZTYqkNl3m`'
)3k5B.;o77G&(!fH!(O-YrYO)t\RK:Oke+IQ?^MR'HhQE[VX/a,3P7=!jXK%iH"/n;];k4qC)Op+;*cCW>;,cGUGD"PZh;_@IoZA&ro1N1W%shDhU!>,
h)7o(YVRA(DVt#eV>hEH:1',9=JVK^j8B'YDQNkWBdo5EFa?dqqkMq5gnAM\VOUYemkWBckIFM20qXfL"k^!@"SZ_N4lrIpACQeEWFSCQ_mnZFpCb%LV
n"\*$+81iF1?TBnI6A:Nn8WJA1m3lJSSHkCq!-$U^3K;3f3e3#huE!-YJ39bJ#O1-=FR^QIgdEI1H66,XDS8%kOAN)mH%Zm?<_`B^,k*,H1?QcZ+>*h#
i34YbIt>DN[e?)`kac+9e`o0Z@r)>R-_*7pn7a_*)<`VH(G+6Z2@i;nLqsCO=lF,Ki:;\B1\@.=]AZg=d@D!+19!&<CPXI/42@VI_cc:'\W(?GK!d/S.
%Q-T?l]Do0=*3(i*R=W39@JGu5:E2bUk'9SY&-[QmPY#a..V8+(<jZg<4eGmoU,apd!3Y[p1>O(>rG<`<XWVTji:m&6rk:rhIl0k_q=WQMnC4sH0e"P[
f#%&OoRW9O#%]e?FT%chP]LGUgq8?&s"%1$%h%GUSQNpp*&V>+-LC9Xk"/0n_XP?*DQNs4`]rufb#UM^U>10%K&ZY[`DKIkH3C11e6KgAVUjCEUECL,K
/CE4_iQl'&O25neW756f6lV0Si[p5-?BhDP,0WqqW14_&s,C-&mPdbZn.pJ\H0(a;QotAcmcX:5"&d-"r:Id'EpbfPY5#Q)+U(ab"!B^1t3TR(W87X8G
W5C1K160?qRAhTAr"W229RO`G]nJ'8PaRVKS[l9-V-cQ9qL1>N>GL%dJK"XQ2RGQ2FMmc#e.7geq_fjGJRRJE%*M4d,7M28fM9$:FsPW5]!h4=kaZme;
l[^Im3.3&XJsb;otsS)aU/PupuWk0n(YQ@4+;m$C`@@K5aMP^'*.":C3V6G.'IGql(\IHFmV9+a(])JfKcFZ<ennH:h+\;+iDu'P7JT4&B)`>SQn)-@<
W\`ndKerWl&">57b3ICj3)pM3-_gZI(GMDE:'S3P4EE8<-Uq'ec>f2isC;T(0eQF?a,WlkTh*/\\$X6?O:Il0,80GIqWF/eq5Wg't-Y@Kk^UL\;k(bOu
+Gg6,Vk2)pT)T-!=A:X0)p`N&S25r:OEgpL4Eo1iKH55rEie/k3N)RUW&A\nM.^642(Ru-gPZkKl-Eh2`Qei5(O.o`QBg=Af_BInJt6&rPNZ^SajAIgY
(9f90ri2,j#dg@LWS#/iigQQ3a;T9c]SfHH4nhqeS4).>[5A]n#Mg>it&p,d2I=T`5D<mT)*=#dhQQ?o1YBcU_2Rj_O#,?3&rW%:eo:_'o/8`?n?j5"6
hFQaqkEBmo$QX73Lb/ZT&BNcV]+#c;lrf[4bk\[&\_1Mu`k[5-c"%jB3aIsP1a4=]H0_U\g9(GQ)tN0#J+WX!5H6id0G8:/VF5-b;"]"h5!+&dlM-DP<
IbFSq;u]p7]YOK6mmSca9hGPmJMQT(a"\@"CO/A-L5rb[\Mkq-\"7)Fn-?"^UqGMgA[0&O&)%8V,e_@FOZ[J#JDh.G]QU%+\/QA8(ho`aSUFTM3_sR]S
'eloWq<]CW/W/V38L=H_-9i^>iAW8["8=F_W8+:S`N@8m\b\Mq8gpeb']Kn/1q.5;r!-aT6V>^&qTQVYP#@\%?JMf8#V.f`%iE8hS)@YQXtf]O,T:8g0
Y7Z!?%AfU&;<^QTtb>i1f/iB;o8<C`RMPt+eM/g0a)D5r%*ENhX%!PU&2k^b+48)<8SV,H?XZi4\5TMqG!5/Vm!S(=\>:kp'Xj5gpJUt.hehAt#?9Ll8
lf)+g&D]+eNPSuS]=:7ufgYR#b;oS%/cQgLB8Mrk[*ei1%^C$t(EZ?P^2glG`;S8/8(Q>LL`p:3.\p!n*Y8"C_]EsQ&5"kgmg..NGjT;`e`FJVnj7UBL
r-]>]mmkg"O'L5nMb']QDm.+pY3H*0P3Z)sbp(ZHhW:V>HY44t;?5qj3?0r>:'!?.rC.hoj0?Fd!m&-9#hM"NW)b$kI6*Zge([%QnGR=riC&ZL,ogjtV
&;id]E/@>@m=`!2i:t,.l_oOn;k]tlP,ABap[65#p"PaBt3WpKTYi_bJBj@Zb]qBn"AY2<JUiF\n#=dSSfcW[2lkue52/N>,R%6=Je?iJd((`J=:^B>.
4<'5'Ch6Nd.=X$J#(,f-:X$lF2dt"$n+Z2F4@o$?K@q_`T71DM[(?RfF1%E(KI!*j"CE3]_hB3R;5n)hM?Xa?7nHK7\rJoN7(S2g.LAZdpmB=N/EIrRg
Gpj]Qk'jE]t5Z?RW#0i"8AdmUnm^JA`Gh@8!*g$2Tq8KDl4.E.Ir$neMaj;MT`KrN(H;X8#"*V`rkF\l?e1'U[@B=hQtB=a:+g%MT4g:`DR:7Ho<mp:7
&Mt(OEJP!=`N'@bqe;A0B%68(h0YNa#WRgt!3JghmEI0YK#uu:1j<E<MU$4.p(>!tp_%n/[\4e(d^L7nAiLCbWecs8PGHn#^h5+uT=D:a3APf_K;Ag]A
p5F6Id<@^iVE(WV2R@FmQ'54^>f2j6<a1W[VQi>ijfoad1hJpDjBA3h(#/q\af;u2cIOT:k)2)X;Gh>PFh5mNqI*Vbi/:cNd:WoMA_L3i,l`)_g`de-!
<R+Sc-9S.8tFZWVfC1Fqs9^\%aPpFC\/o$Z4&1CV[5O+Y%=:K57m)l&qt[)1jE)c;sMb*gWa!X)A8iSY%`5-mfmQ[q1e:2b+3_(AcR?;_5-ZhGM6'`%A
sdZ+GTW,89fnQbVhD(.n6W,+I_-:$B[0mO(rZh\(>f@4e$>E=cV&ma8hVL2B&piCqtYSDMn]#Z*2D$CVp.k]Ar/*Z$BlL_6P2M=\/K@514I3^GaXCJ`A
Blabpr4"M&GP>S+i`P$0pKZrUt*>*]&,FlBNl*[kk9M&+Vd='2@5qEfs;()Y%c1,_=?%r8)r*8qf&qP^f=Kq`=;<gBE_?7N!9j[<LQH/1%/o5b]d=Y+B
aO(^O;cR_RCBB)lpjsSm(,c]L-nC=d`kuo%4bOqk]$WV*QJp+\lf>?njDRRcclW4?iM?.SrE?H1Of2$lUI$=>hn_0%Q3-q&tn"JD*h$kn9.]Qn:%g&GI
5.CUF@6gel5N68[eZTlDQ(t2STZ5`chFnb+"s(`MgDH?R(?ZsJU1LbJiM4IK3`Dq,iiiK$q8?=2ib[*6=KSPm>Gj@t.%.:PNpD/e=Z!I4PCUl/&OHeP/
U"8[if!5YP2?XEJ`%cE+;rec3JOeED3i<Yf!_([TOV%6XOYL957)[lp:I$hP^usVbq1b!'=h+RRsB#8o!`o(E<(^XV&5V?p2'nKJYu5"=efbMo.)?<!A
$Kf9'N+D;",7]"mNU<U%28t5.e^5*j;paWB5E<=_o1n5-2G!D9MA6U'2WCS$3(%%9fRBTImHdHo2O(no!RI?fGZSRI^jZBbS+9a!%_3$lTW:[$*@iRJI
EnkE91BOsafWr]tJcGPYZ#`%;QJ"5=V_[+-%Mb[<KjEq4nMrs*O+g8_L??d%Q3RTDmZn?je_a];F<Y0ac"rki0V64F^<8]n9d+1YtTghSgd)JgdO(3uk
71"m'M>Yd0T(=qHr=*iM@>%'K%?2J?P3A<[aZDi,9Ua^#R"9!2\WbHI759V*V9)i,/qIN""X(>"G%eEP]5Mb$Vqs(l(HA+["n]o)YAm"^SIUL[R8d!t[
I?Pjt75jUH%=<b:+6<&WiEU++@*MfecW81'Mp:EbM--D*gK&Ze>7<9P,/R*^&j8/G.R2^Gf,0"XgH(AU<pP(NMdBk`/QL_/98f6U43fE/PsrTTgPO9ae
8JX2SW@u&A"24dB98SF['@3@fn0/pgDEA&gKJ9`<HY\-Oru8bqCKG4&ZXCgCZtX#?cXG?E11:1>T=-`@plun@?P4Q<)C`)7K-M/p+n;a<h21\kEr\R8a
SO&hi[qRYCX-/`b4Vfgj98&^GTh'@3,(PJ^L$$MoiAN!d"E:a0cCAqH?V'lDIBaejACk[DdP^CXXm$VKOe\BY+D*aB__Qg;@*$`D*2rc+E7;55D3kbKl
H8A2XCXFXLEO\QF7:?8e?#hB>=tZ.Wl`5[D-uY$!ftY#`,2]`O?ac]NCDgFV\Jh.,$&Qr0i>pQu8h97W,U:,2e='rt/>$#CEd(&)"VTkhP'$J+&4lL*Q
WYlBGpBTu4dm.p$S(H6TCJNM@2lM18?@"uEH`4E2YIsktt]dIT9R,_FKXuUg7mO(*>J*is`lmGrX9i8V2OT*)JOY8>4q3na8aPkl>CR?K[GEOHmHR&Eb
DV3Um=/IQBgWkVS[>4`J.T(BY;@dZV/FuYc];\q*Cud[1h(uN_-g<W*1MC`J/4T%aYo9,Nf6nS+)=hQb.(kQ3.[K3Td?u]?@`LmACXEM+3D&6U#._E96
sMbLj%V:T.\_Nna\5BOWX.F*;S;$X]X;VNoMhRids3udB4$<l4)0,ePQQB/!P[u.'@"a2X"o?nR*]qC??&7om#>nJa`iI,A71m8,Y*TGA?eMk%W(@J.3
`>@.pnNSBV(ph`@cL<9f%L5J;t>RT@,8\Y>%r$-r%V+%Jb@320s5n'"rWngpDZO75J_T=&hHO3rTmBhLZ?VO4#3',)OFeQ"#Pd#pSC6%bnP&gL9KX>N3
dgcFVf9'+Ad7<ONbLYIN/]"RM;JeHeH]94=kTe-OGsHo1ThXt&o*A?+[QBik;^h<ho+rQN:)>4KC1I46*n',308B[2XW[j/7h;e/>G$"^EC.Ku\6)6]n
u8=[0lJD&RsWR\^:9/e;FhO7ZF!gbpRfm8f+.jp)gP7"rAH2)2u><B9*a=t%qMV!b:GAWm$-hT8MkPhTtXPA2Kf7YUC+.hSPLZO6F+BS)K>'DjNcs7-4
7L$p;>->[s`M]C*BN3r@I:Vr3m!+)JIQ-K.QRp=m^mq)j9Joq63C9GV`]!hi['"j[]kmK1puTW`_e5qD^RX;CH'h)#6b@sdXoUqP$;f`G#=c4QF/rQ6W
XjFKQM7iVmJTt5cYkt^4j@q&+ETCUcAacSr%[U2XkH?/P]t_8s/dC)@>pP[Aa]BD!X65h\t(FXs%e(A!B.lCCasU#,u0#4%.\R^?onrh4-)e;43U4;Pr
#4fXDpjUE)bS)ae$7;<cRMU"aCD3;cB3q%n?6cC/C*Z$-`KK&PbQ&fJ0A%]Q+WAPTCcc_H3dHbX8N*c.-*3"f/G4?^'5sd.*]*a/_#DTfsp.otB/Uks0
8/85H^o9"C@Sp<P_]qlLk.l%\:(K'hfM^bSVBIAZIQLrH9\YkIIVC1\bG!BXrAW5<?pG/N,Iq9Qia*0Q'e6K1%:6]IR4>CfiV[9@7^2JDglZop*QrokT
8mh#S)_W\X$)+coY\c_k]>Wt`LMb6(7,]1)P1gnYSH@/_O&WVKR`(KfS:_bSTe%e+Ide5j,kLrlZ^B<5%FM^6o>N\hGNJMS9ag8GhAl0=UlNdp.-\`CE
p%mU-CA4QMBs%`R1l8#Wgp1u`)d/+gSCpWZij$j>)8@T6^^gA^g>NL`iVIk#;g\[Ibjjpn4&'cHbH0ti<2kn5d3*=CRJA'P2/Eks[ML47Xpg[3aM'G/A
LjWu]E%6rRh:lZfRm=uc0["@\e^"*0_/rnWF^_Q(o>4&HtYVnR4\<2l=^TAjn6Hmq4_=GQp*A:+p2b<d-5VbR=Tq*^:%:cIoE_-Xal,?)0P-g2m,qn;O
)tN68c+EkK[(ZAgpml#8]h>2SkIO:7ObL@OCR$GA3GHi(RjiQs[JICal4gj&K:HN!+7^qBb/?Smb;9Rh!60]N@lH0"#m=rW)D^c*J+2@Q@l&8=TKibOm
RYZTYV<^7j8!]tS\Xfl$OR:5,!0hn.$Oj;iWbEM_AYEoL!]>$OE12^:Vu&go#</OK-6$&NAWS+U#.]kTlF+J$!qJ6(OE/Qe)@A$E(+SPOnF(DKfs#oR>
=H>F]hO(9@u,o!h)W7S3$Sm%:p=Y#n"Z))KRe$.CB9+.l@=lNW/b;-%)arOXhHdHLg$7h^>\[SU@;:>CQ@U4K,QVMU1M!c<3mk$]K$[<-AQGljTkAY5k
=:+UcW`p.sQuiHXI`hd%m7le6F/Y!%C.DqgCjEeD#!_k/3Bd/>[4t.9@=u@BTW@SaO-hTrp7=af3_)XMEf;0KBp!AQS.J^`YB*FZo]>R7ZmMNaA=87TB
4)H$%=P#lS%(E,Ucj.%/p\CFhQl1#`!$">>>:L6OpA'%eK0>pfW8a;2T.'X"4%SIR&e@:#BkRH1SIr#;%"8`Zs6TkCH[^]"]Mp6(ENaP?__.'<k<Xd>+
/9_aUNqe&m220m^B-3btVj4M=ZHq<Z(Q"((K/>Ga*.>2*qaD=;scBdlatXo%h$(fL:Q-c>d(SmPqcjpXC2U$c,4lA8X9qF#E0&cWM^nT6+uKCKGWe]1g
03-jp;u;:T_r$,t+A*/U(`#)X^U\q36<p855Sq/$4.s3FhJD-b=*/$'5!XjO3k**c^opBZ4b$^%&&#eNEg%<B\m,.cQ``rFjOb""7aBmH&rN>4_O&cUn
P,W?q?+?])4p5kYQ&VY2c[*D9mdO-)OQ2)uqPH'ShF-lL2!BL-P3"R=HCmAQk*3_C)bO@E&Juf@1Psr:;YT^5<hcf%p(?7[%%5h34>4P!a(aKP8]UWN!
j5i_7b&$#[Ct:j$_ih#DVH'l^WNVAB;9`j,`+[E0^PrTgSD:nn]0h_:AN)je[^*6HAe`+ioe:0S#YW?ANTYZ92YkZSA^WI^Hs2?gX[ZD]j49Z(4L4=4R
XG<p,ZPXcaf;1\/1*;9[RYUEobqh]-JIjMmHuFY4h1+!DI?+BVN4`n$Y-=0B3+-I`[BNb,9PD]PrnKnHHE+0m-``__o*8S,h/QlfDSBVabe-lR`nS(n\
'-d9T9L.\Bp5[Wa*a'6(do+!nl.P>;nhAPplkCBSPQm@S]9dC6M9tm4@#o0?L_EX?+]*DH4?q(9_e%T2<BScuf^<c1/`B^Hft^nlUh3j^sX_iY#n"%7W
[]J6n40HMLhifgQu1g1c:;NW`%##/'"oXN,Bt;00)Z>/7XDUi@-QS>aRB7;T$$;DS0e=R)cG];)</;9rqh-r-l=0ZlCUQTLZ%P]Gi^V#bTk=.>e/b=p<
rPM*003R<i@DLITQEY#'"].\-A`<M#"WM?^ZcW(<E[B^F!k!Z/[(>%s-O7U/Y4$u)rgCV4UZF=S9?u_[<$_q]Xp\*E7qW$Omf83;+oC2J>VMn:eT%ESt
+8#DWD%$G'P=_'7dDQnFl#^>/n%\p3r`>U3pVGQ)$!DXq[:$237)"43Mt>5s`?2a:&psS0DqZRFBN7u?]C8[i@X8j0'l_I;[7i8:6fi8`CTlX]A'kB2\
g])H,u-Hom6@>:fZ):6Gs\"fc8,HV)eXYtat_jBI/<BhCPJhg7A!ssJsSI#JbSUd-^RaB8Cm[k])]eKHSfrn%O,ludD\5fe`?]rQ,o>s8MmsP,D_;t<U
#4O\loA%OU&ZM!lZ`L^LO?FXgKN41sIIdq`MbkD"DgmduYG_B"J<9S"fsK7`R,sfCZSnp:#3L<kuChEuFV"$0)Gh55P1&,g^YLMja0A]Rs,GQ$KfIj!;
ho$05uREuE5'(k*pBh-!'b38i-kYZfrb9-S.P3=+"Vn7B-.aQMNJF"PP(BJ4AlLR,Te=SJRMf<ue,:tW:3`g/h^XQTXS5J2m8e]AOtf*"k!`58ij+uGX
.CCaFP*->+C?GiAs_d\8.To2X2gMH\9iHXSc,K7Hn,kRjRSGr''nZ*IU[P#Ws2p6h=AW_=;l70Mbetqhm8RCFCYedl$A^$&*P@rJr:GQoi:*[NmkGFb*
C[9Y+=j7.T/S9!E.ATaNG^Z!N^)CK&@MR3Yh1+HcnRbF2'JQRN%*u\<6,@H[95d+)J!N+K)bOH5R+`6HWNGg;iS/Qp?9LB!I[IioqVC+gPN8Tjn3sGIc
_.gmX<OU"NAi25*W*jpr)V$Yq$><j4WTTW_F5FSd`=\<=!l>)qKC?lS"%XqDCkBp:J>X".^_J..=%1`&1G3=:Dm7s-mTl<7`mPu_^/rBZB!^BKl6Vn9<
5qIhJ$^)d57ntITr^fl</lh_hb<o<f'(P<d3WOB*6>ql<6UH&f*Fe?'`NM&Oop*0[g@8)Em79-.gKSn!6`SjI!5M5=+JR$j6*GDL]H1PU%XY(+5])5/`
1Cs*)2kF9#*TN"NeMQ`g7K1']MU&Zc%<Q'I7kFS_cKFMe>E9T/1QJ5%Iu_2s9?:s=Z-kB3#+6m)4F4OI/o]9h&UJCTFbHSE&`pI9P<Muqp'<U4F#0;Sj
3^!'%F\8GRS3SkUshHKK.Q/'2G/d5B/RHhff^^kcadbS1lNh!7dcSF,R=PHeUH,:Rt@?k,9ee0.5V8<Kb(q?OXHR<*Aq:pq2C<;4#g^0_Y710<"1+p8.
SgfXF</add]NJub7!-?Q\SQ,[\jJafV>'NFdi#JkfBI7BMK9k5o0^]J]Jc]$(i5sEM8bFF>`u3)V]%V`2hb_XBb-BXa,9DHY!OIj$Euifd.a'PW^D?<V
a/5tQ[t*C'L[AdilG@R!a1r8;fa_HorMgi'NhAA3@)Mp!GnuE+hLb^`_n6E1?LRH$Li+`W1^*CQLIlh&F6]T?H(oFNN=fU>Ep%HC?,'c*p-GSFUYUsB&
!ZkAP]-d_B4Z=WC#+!`cd2+C+_"3.$K)2`3[Le2Q\7CNOg]6X@/0eC`=,><GZ`T8\KbTdUr_6Q;u=<1Q1NEOpZ!5--ECSDHM#+#$>&Oe03Q8LAr[)&:,
!#dQrEu`mgf^[!C,sgY_fB%ElNm=@B[XG*CS4NIKWJ:UR9?bbXV1VSiC3-(cTN%&tm!2jn5o#Cr2](/nAZHE1b3U%)g#r;rEZ8ug=RIt\oIFS<9?lW,I
qi'R?HBXqBDDq_QFXA>ALJK#>%f:XG]VUL)JJq#*<*0"_P[P^*D)Vp"CL/RGQ@,3$F:9cUF9!;?>X5u5*NN?5W:%;MYNQ/ZV<cI<s\i>(cNQd:>WY+"N
5*[W6S?@%LCeI$R>3,ma'#fR;Q\q.sHB97cK?-="b>iP2)fm#BN^s>_He(sf^q(RV",W/H#_GH1W-k,/XG.OF4gJj*c8-t-`WE?j_!kuX5K];f]Jr]%$
E&]R6uu6m6))!jApj:,2"G-7?[f2aU;]#WJ\KQ1FUKMb<QdR6ANbd5+Ak^ZKX^n64sTFO1")u7mmf&JQT@X9lokI_+NCYu"@+0CjngU9.ZtPp)c)R9!V
9cT(A_7.l7?q?ma*mW)G_2]jgnQ*A<`qk+iNrViD_:=hdK1/&X*#W!4%@CXUVJ5@D,sr83&\XG5UY$M'-@f0?/6(R_3Pb4b3f]X4GN;;2]E[`Xo]s,l^
!*H:+qnn9SCB&f8PbUc\'Dk76!H&qnh=L'=E;8ruC624T)G'6<3$RnF:c6"d:WY7;sG<rd"Nn.<t6n9"0(FOqY7Ri41LhECphV=&>nV&bilE@YA2MS4p
qC7)`n2]uqZ<Y>*>%Lm=)arNWJ:t)/*h:4Jj5\=b3M\"_DJR;ZJkhKaHn!N+6a]@JbGeKk(*"KS,e6s/_o*\@4=g'W4c;KIRa;[P(':JrH5GocR[2o4j
W5!Gf6W;@4V_8RE5<OAama(sQ19(DS"MA4sU_V%nH@'a19:+)jFrU)1eU@bE#dQ/im0s;*_g%1Ss!kW352aD2m:_q#UaQs\TRMC_@OmP9ju3nihE&UA&
a@r7R0ZcCf--lah:fY+Ru\BSGqVHSr#O;f&A[T=M!9=_>4_+e*>=g%n4B;(#$B!L1^,b@J5Ye:E=uZ^2J5JVf=OGDarEr'O=rQY%>l!IZPuqRFHo5`Qi
`hj@?OR#&'UhS!thJ5QZ+;U:d88K>[XE`;Dr`^DEGEDTrDYX.:tR"oP=sN(Q:L>cBHL8%UEfCW!;:VpdJTMV'ZAD>WLgNh@/97\I@l3\]_/OXBQgZ(u\
LhF#:,=hi5:LMp)NpAMN8:D3I914dtL5QqkgqA6K`j8._9WSg:):f3j1@C*;_[4(K1rbB/!q/^"P<N/e5Hj-9cX`jLa5H8mZJ_UqaP<O&n`(A^+c_pR0
E+;qmP6O4>9,rH/cUkT!h@k'0tJXU^F'<b2tBC,PkGm+.4]E:Na!=/lDSKJHbD!uFe.s2o!hMn>eHN3!\4?J#f'#_`O:Z!5M,"DV>k[4<i/?`.29aPhi
8T<*5rF"Ak?qdNS4fd;Xl.p#(AM`G[`ukI]Z`poXC?+d6U3D]:9qCfA__RMF$-"qDQYZId<3o#2$2'DpR+g7Fj7^qof3lt7C9o^(PZVd8$kLML90jUr`
`$KAjRl."W/+Z-%g;=uS6%_Y?"^A+]N_;?Y3`>G=\<i=S<sA6q/oH(2#P;$Y$5<X(Vn^1-[SCBZZ4')[<uJUPuE,@kn%VD+2+UJ@pgi8mgkLXai'0_gi
sKPYl"2l+*ng<8R3Fg&B(X_^2%aLV3$uXH.1BMILi(]AL56_W:dQr[8Qd9SJe_f:gYsrmg.95j]rN_8eN(*\Z36q#*oTQR3'h4])D.>D/-[c-daiE[I7
:UR4KY@EN?6];5B4d0^[=HeeSm4fapDZfcW.TT;jRR487m'(XB$E65dF9XnZW&l/ns&ga3<P=YX5WO-Hb4Klg'+8&bnPcqFC9cgVrdW[ZhO'b^SPJ/+M
#pAC>[rXBpe[[],+V%XVa6DLf&0LR%c!,YG/)I"AX'U>qF-Z*%[1L)(Ri9Ze'=H6]4s$Q#Q[uf4\Aq^h.33ii2Zr[u0e_"h">g]Z4]RfJM7<apVF4Eg+
>E302O.@p!Tb@OrZMZCZXnAVp&aNp*,l/Q).UnNs54#Lj-1q#;qAB$%)Eo+ZKnGf)jb#I><,p00[V>l7rL5#Hj7+5RG630(=BH@GB=/l5<o6kI4"`o;Z
0QDsB%(_oB_6ZEiTStD=3%M]_0W6OrG=V8^H8)Em`25^Ndu\t2Ghpj?$C=,GhjSoo:X;mJE<72JJi!(18O]rUs7tZCh(<-T-`!1bRd<SQ&&1:()]]8.d
`<fhaBEW#p`l5%n<C,@QhC*RI_[[*O"5'\od/OEJpsN8>-8HA#HuqpLb;N-Tot<LJ$s8O)nR3&3SlmlLI_)S4uN$OT*/si2$_2"P,uKChSGsFb*`[oPQ
RH^?GOe=3,lJdZd*p*riZ:O:mn7n4_c1TsH1f^k.E_XOn#p9j*=H@9)8"Cra-,LT@b)8&@1+R#fO"M!dka."6WDdAW,><W&)A$m`nq_^qZ%2!C-cO2YP
>Z!#C6htU&I?DO=Dj@"Yq@#OJ]N[_i9=aADC[jX2Y-&$7s?L%EFZE2-9FEm_s)bMo0.Vk&H0%\E'UE0(DVi[K`((&S>*Q<o#\-M%o8p;8,M)l!8>Wh`[
^]3A![UI%!2B2^QLE<WAR!4dQcNm.E#FMF\%HQ@:!`gK>KLT#r;+:-joet-.4sKZLr7Cu:5>Im-`;^qZmJlj]V,+4t?DTZHX4)'VNu&"HXSRuSl1[@`T
_/'*q3I4kfJ-8$54P`s?'(U25L27a;@T[Lf\]4LOZ0BUC.?Ds)lS`j^O+<LUkubLI0n.&jnGWu>F`L&bMkQBRueH^SoahdZ0;FaP>SXR7VJEu@5_[5>\
scL98)sO0Y20qf6dl)NYR;r#>G6L)obl/-l`$OZYP'/&YZ\bdY1@@T7\Wj&IcOmV'qhT>RNb_F\1X+I65'OQ9,K?M^2<8?l_!*<1U;_W8n(ViukUe&mZ
PQ/PX:9i0Ati9;fZgbg;BD_hJVk$s1DJ,8!2P<KWrRPW2'+>EEo*02_7N^p,r"?0U4"35i#-h/\XO6Zao_V%R'bFCq31IFsUSiPjplk8<(YP9PYLU<I%
[7Lla-i?IcDe'jBVZd[C^Yh/\oZp41D&)lulFT1;+2'n!P,o1^be$BS3/XZPe?2p)8o<C&-OXO_l"$p-6(S@BO5C4bK;&k_3QD)28\KYNtL).!G9;U)=
3YF+-6MqHsf95TfR6Z[Iht-RE9'j&aWaLOb>jG;#]pqQ>Vbu,!"F7AuZUs:_LN/YoUrlN[ir&BMgFX8/Zi,D;0S%VB?HTGa[s)S@7VLLW:FJA<jELG&F
4K#b"@fPr5_QYqG]R,@_=BhR(<QbnA7#oPlRaY['rupoEg9-_fhT:*j"OMF-%*L`H"&"b$E6Q`o-^Ek+]LIZ/+:T83PeanlQYG%JP8OXM68ECH3\tY8R
*j6ZUJ5sgMh^&9r%Wchi\-)N8hE*LUi^smq)(J8?3Tp/dQ,P@aKKK'j^2.@r"e5e$eq"+*8/Sid"]=EH*TI)OtJBdDZj*EdEi59.!Tue/fO0i9[1WCBh
,p2)e+l'@pc<'0:bt!dS3KTe:Gr_[LY:8:N`_(,fXCE6$TrNa:j*>R),oB')/%1U;a7:*J.,f-6b>mRsc$+p@'q5/K5"1Eb8jYpc`W6O$j8bS=/9Y-d7
Jj$iiPJgt?2C!J-3dF0j<bCF`?8pp)?cQ?C+X8HnOFtcCsq:',&r.,?LcEuIC:VA,1Bh>C)Crm4pe;3a/fIX=@1Y?R?^/+KRXUgu:E8;8OfIKB<'S0Qd
+Y?Z?'fGYSLU5O6G_agiS1J`ZYnG?56sp;9*de&h)!qRQp#@H'7#_'N7j5DKB#OkV._[4WLebdL;fNX<:>CCU/oGL\Ob@;rF[*eV_l]$FceF8QXUNYXe
GrCudqM"80iQP$FDUXS]<N72<L7q,j#pKd>pi<sFf]3=h2l9m-Xi_/,,$=2"9M=!OuNN:iF&Ni+i]F8k2XXkl.GkMG<QN6,OI(j!A<0F.^8t2#>bRN=b
;FIE^%)^T/i8^C8r[%3390Ek]2[XYeCLc=D\h`01En(=:uFZ7`<G"![E*uMK&oU;pehe2f,E2j-8uS-jU_@_OT/V82-9H!et_uO-i"*>bpZr=iR`e\7&
MQ&ZnfM%Ua$q]=tF@Foq?>hg<0BNo@(*e\-TAL4;W29oJR\3@e5:?^9;KUC0<oQOQ/U*JSa,AB@,#4T-Yoe?o9EH7QD^=csNS,/I!t8apTPh>\63_Jd?
MgZ8"6]^aad:X_#5!(OF^_h\2?$N7deROVoieJ36qZ[=L(XgZ^t=Y5B0.S)9IN;7-D:s'0.A70jbIBIB19n[mb2Q'rp#pjcjTY,3nMjmoseP"b\K+^cg
j*(LN."7"q'<$>EQQ^_r=kP)rVc'_A.\Q1QF`SN]&,!HTf[j/Si24rVU>*],%`^ji8aW2iC=_^O[a!,6Y(iND8?r.;'gp><Y5YkGaQ6sKc+J-o8)DgaG
/Z"38HZfKAg!bAM/[/VdH/Xq0m]VGWTf?u,KfiE4J,nPA97I..gibS]$"!i%Cf>-ZjLOgo3ARm^MWA/((gZKeb;9ko-78d_UJ5VcW0tI6n7rOjWr1Na<
r(P)9bIqrQ9o",lue0cHt^&q!UsRY@(CR7c^hH[8-cXqPai3Z]WHPa>n"1@=rH"k'SQLR@c=WVLU;OH:*s$R>Zh'6:`@o-@@,D>-QuBU3cquRk3-4o5Z
Wi8*W'I8IeH-qUWoLaa,$#eAq"3UZ5uOr:0"$a^:iG(UFAGO782Pp%Vn\\Iif(6um/\G$]&5*6&5YVF)V/QFbZeBEZE0(8;/<fM]o6/tglU"-UL1)klO
I%i@c,WAod5lolFk2I$Me=-04=ZTr7e!d]+>;jZ9=52O@(n19W>5AJ"1c]2AFHhlsFO1sl+fsLC5X#p*N([?p!Uom3Me15fao]d!f3;B4S`Kr_D6h*^n
ToHi7+2C/<h:"=IG;"uKrH+4ts7lKkq2`;j?iTouJ,[LGs3!Y+ra5]qp](+4J,aHeq"t*O\'h0%c]4#>1Ce0oEr8+*_[`jYXR_M2NB9^Ys7>.Dl=_<0c
V'-k@loI!=/?;":Gm83V7(2of]@>q=K8leEi;GclS9JR(nB@aK7[0dl4V_pqP$IdEqU)3?SDmm?;C*54?'$.16Mtj@R&AOc(nfdQc=TC-h5H(;9UW[L0
?$b!)V>PlV;U!&cIKSG>jj`Lj-1?'j]Qp6434W:rh@^MTSWD'iV/kLc/s;+$:[pc6P=Ys!ZhtcWlQQn4@!)R!q*[Gi(n!_eSuLWWc?ZX;!pV'/:`:[O>
p/Y+&fc.t)F4o].Td<57$W0mMWGitj'W[(;1O+Jh").YO6\#@Z8nhD$ujs!qJ<OoMP%Ld=^"!jMmU_K`3iP/#LWB1d#(Gb<r[4WJ^YL<b@/20kZhU:Ka
kCeQOe?lN%;-%$J5-piM0.CjY'mDh(Fi=!'a\_Yjb/4j<IUE:F47KR#D\k.LDP7ZO[O?t"U-*G+#_C=-AU5@Ga5uiG-gX`H).6Oe_p4!`8ePPKB0/k[,
EW0YjEW/kjGYr5A!DdC_=)gF8>>$5L<s^-[c$uI?Y_EtBn7)ZikIiRT.TK$fK-tfbi*@'Jf_A;VcW50s%5=c*"eM5^$^S$@0Wm)bPt:\9GDmpr2r9(o`
A@RSD>ig8HH,,+d;al3/(AU2/PtlU(o-8pX=Vi,1%!0ZYaTdmb#/Vn7&\dl'o0._if](@KUA(e425oPOeGFSRR)UiV=C$7kEDo-rKc"Y,]rYf4.4cnVk
K#eo]*&t_tDmS%;<LFj'UsO6;^ib=JLX0-49k.Q3?p7N)ZIQ(G<&E"<A3%p3saGDgHE45J-UMqGko2p%AhI+4>"qJ@ZDKiU,gb*lqR)V=*b;a"Z$E6d;
_>b4m9&fjNmd&HKGe<Za*&VP-#q!&?/'56FI4hWLI`/uS&:g3+u`WTORS8://^7]D$NShtD#bg`nUGGI4T`36Ejl!#pr&91;Ii%9=#cW#YFnEEeE4hKa
d_:8X?'Rs1u;bG.+?@=)"hQS\IkD)fbgkMCkPY!2p!u%KMg^9]\(rC?0HFVio/g5?'_='Ka2MC7pJMW#d1\/ML9%>>-oAdQYgP8J."3i#dTE.)1ZK#?$
@RG'q;cTur<Y&3ZE>moU>4UlBD)]t^\p:c%eB`mPi)K?;\0$L':-P1h>'qN5`FnjqYfuK-pY1,();UJ%WO/cmC&=m5Wc3;7Fp&-iM&lefK5F^3SrMos%
Br7M*d5/eYD948J!0H=@Lhi%(6"-2.r-ZPe!@gO3HW23;L4IMBNtQeK.,amLSM:Z/Z&(t5c*4E.W9:r8aX]$Y,GCg(8Im\;k<:ChQ\9_OQtn4*nr0epD
69gI^=.)Ig-mN8ukdB]3;ug''bC_;!DgrkQo)6meUt%aXA?,S%-82;[boJ,Yr>fUP/Ao5BRDnlY\crajo1gZ%N=Gb]re&86K&tb^uff*-bbtn(4<s6!R
MhRC8^M?"hr6-9#m4!CLoXh;$M?bXZ)hejjdKS*`3<PF65J5=KZ+@$K"NhX9&KK``5(.Nj'e?-O$XQI?0q]*tcd9V9EiV&EHtn35mn0Wt+81rBjjbYj.
phn%amU^+39aQHnS+5)[P?\"lt7SK;f-*7WGca!9l%Q&G3mIq+)i&%m3>8P)"ea@aCQEJAo2*?^%?K-/>Ah$2$(\#M(^/hO<oi=b_l6dug:37YQ<KEg>
<:PL'bc(HWo1aNS,GJlkrcI+C5Q!E-*IA?F)\:h5T!+L6hl_HTq8:t=LO]-kBUBm$^(%gtSp^i.0`@YZmF5XM=lemj5!FTr95],AmR@,%5OM&@V&pdIr
ja+8MYsk(IhDKL5Q29tT-&Otq1&"rY9X)$O2&5*B#=li$R'nk3D(NtgfD.U!B5hGdC%D(l4)C6Dp34j]3t\"TXusa.c(5:cMa]479%F.QjXEG(a)f<\_
d6-0<mRUK+,:?,?DEXE?s.gn@Ocd(J'%D:"J["";51iQeU@aCjkA7?Ih:.7\8N+Id-fmJ*/%*i<qiA/q,3&PQTKMh:Cet[*=ca]6K1r9Fgdjq`V'dkHo
\VJ,^,H>`*e2j.aJVKRpDs6Xen:C_+TjY_I0-'l9p[iBGf(^Ma\ppZLL&Cl;O`WP#>[*7e_3ij;jZS*m>GR-][dbY.P@"hO2nMUfh-MB&@Mak$YaA*ac
MR$VKG>Aou$33O9aC#?:W([*kSDE/CX1g,:j47e)ZL><nIEBT(.-TtZq+G<sk/njY-4Fq/n@d%R289tAaf.<[5_i!<3rL\*p3f*a$nFJ(%It4.E@fJ%X
Hl;gbiTI8o5D5Z4A,e4Oo1eTO3VRHO*Y;b,P#0]1$`&tE].&i0#sSq\f3m!L'S>Nm"MVl7L'hg,;[qaKm>YDrE&"r[1HqNqc]:oA@2"AQBm+WdqodgWh
K!8>YM<.Gl+aB]g5`V2VPBifYVHa,f%+Uq&+h-`SKf.?VJ24gBhH2a;a8hS>1gYeq#:Gdp6uc'''
	exec(zlib.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.67'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-11-23'

# The sbin directories a non-root PATH often omits: smartmontools installs smartctl there (e.g. Debian), yet `--sudo`
# exists exactly for non-root users who want SMART; and macOS keeps diskutil in /usr/sbin and mount in /sbin, where
# cron's PATH (/usr/bin:/bin) does not look.
SBIN_DIRS = ["/usr/sbin", "/sbin", "/usr/local/sbin", "/opt/homebrew/sbin"]

def find_command(name, fallback_dirs=SBIN_DIRS):
	return shutil.which(name) or shutil.which(name, path=os.pathsep.join(fallback_dirs))

SMARTCTL_PATH = find_command("smartctl")
# Not found: run by name, so multiCMD answers 127 (statblk's note names the command on stderr).
DISKUTIL_PATH = find_command("diskutil") or "diskutil"
MOUNT_PATH = find_command("mount") or "mount"
IS_DARWIN = (sys.platform == "darwin")
MOUNTINFO_PATH = '/proc/self/mountinfo'
_DEBUG_MODE = False
LSBLK_PAIR_RE = re.compile(r'(\w+)="([^"]*)"')
# Output columns that come (at least partly) from the lsblk call on Linux.
LSBLK_FIELDS = {'SIZE', 'FSTYPE', 'UUID', 'LABEL', 'MODEL', 'SERIAL'}
# The columns the note below names (SIZE and LABEL have their own sysfs and /dev/disk sources).
LSBLK_NOTE_FIELDS = {'FSTYPE', 'UUID', 'MODEL', 'SERIAL'}
LSBLK_LACKS = "FSTYPE of an unmounted filesystem is blank (-F keeps it), and UUID, MODEL and SERIAL come from sysfs and /dev/disk instead and may be incomplete"
# multiCMD's return codes for a command it stopped at --timeout, and for one it did not find.
TIMEOUT_RETURNCODE = 124
NOT_FOUND_RETURNCODE = 127
NOT_FOUND_HINT = {'lsblk': ' (it comes with util-linux)'}
# What is missing when one of the commands statblk reads did not answer in full (see cut_note).
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

def get_macos_diskutil_info(timeout=0, unanswered=None):
	"""
	Build map: /dev/diskXsY -> info from `diskutil info -all`.
	Only used on macOS. timeout: seconds without output before diskutil is stopped (0: no limit).
	unanswered: a dict that gets 'diskutil': its return code when it did not answer in full (124: the timeout stopped
	it; 127: not found; any other: it failed). What it printed is still read, but it may end in the middle of a device.
	"""
	if not IS_DARWIN:
		return {}
	info_map = {}
	task = multiCMD.run_command(f"{DISKUTIL_PATH} info -all", timeout=timeout, quiet=True, return_object=True)
	if task.returncode != 0 and unanswered is not None:
		unanswered['diskutil'] = task.returncode
	# Blank lines split one device's sections and lines of stars split devices: a device ends where the next one's
	# Device Node starts. "Not applicable (no file system)" and the like are no value, except an empty slot's size,
	# which is 0 as in 1.62 (a zero-size device, hidden by default).
	devices = []
	for line in task.stdout:
		if ":" not in line:
			continue
		key, value = (part.strip() for part in line.split(":", 1))
		if key == "Device Node":
			devices.append({})
		if devices:
			if not value.startswith("Not applicable"):
				devices[-1][key] = value
			elif key == "Disk Size" and "(no media)" in value:
				devices[-1][key] = "0 B (0 Bytes)"
	for current in devices:
		devnode = current.get("Device Node")
		if not devnode:
			continue
		# None: diskutil gave this device no size (0 is a size it gave). Disk Size first; Volume Total Space only when
		# there is no Disk Size (kept from 1.38 for an older macOS; macOS 26 prints no such line).
		size_bytes = None
		for size_key in ("Disk Size", "Volume Total Space"):
			value = parse_bytes_from_diskutil_size(current.get(size_key))
			if size_bytes is None:
				size_bytes = value
		model = current.get("Device / Media Name") or current.get("Media Name") or ""
		serial = current.get("Serial Number") or ""
		# Type (Bundle) is the word mount prints (apfs, msdos, exfat, hfs), so a mounted and an unmounted volume read
		# alike; File System Personality (APFS, MS-DOS FAT32) only where it is missing.
		fstype = current.get("Type (Bundle)") or current.get("File System Personality") or ""
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
	instead of piling up another stuck thread every watch refresh. An error
	os.statvfs answers with (EIO, a directory this user cannot search) is
	raised, in the caller's thread.

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
	An error statvfs answers with (EIO, a dead FUSE mount, a directory this user cannot search) is raised: it is
	no size of 0.

	used = (f_blocks - f_bfree) * frsize  — actual allocated blocks, not counting
	root-reserved space as used. avail = f_bavail * frsize (space non-root can use).
	FSUSE% should be used / (used + avail), matching df Use%.
	"""
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
	"""Bytes from sysfs (the kernel counts 512-byte sectors), or None when they cannot be read (a device that vanished
	after the listing): not read is not a size of 0."""
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return None
	try:
		return int(read_text(os.path.join(sysfs_block_path, "size"))) * 512
	except (TypeError, ValueError):
		return None

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])

def parse_mountinfo_line(line):
	"""Parse one /proc/self/mountinfo line into (device, MountEntry).

	>>> dev, ent = parse_mountinfo_line('998 997 0:34 /root / rw,relatime - btrfs /dev/sda3 rw')
	>>> dev, ent.MOUNTPOINT, ent.FSTYPE, ent.OPTIONS[:2]
	('/dev/sda3', '/', 'btrfs', ['rw', 'relatime'])
	>>> parse_mountinfo_line('too short') is None
	True
	"""
	# split on ' ' only: the kernel escapes space, tab, newline and backslash, so split() would also cut a mount point at U+00A0
	parts = line.rstrip('\n').split(' ')
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
	device_name = _real_device(_decode_proc_path(parts[dash_idx + 2]))
	options = [x.strip() for x in mount_options_str.split(',') if x.strip()]
	return device_name, MountEntry(mount_point, fstype, options)

def _real_device(source):
	"""A mount source under /dev with its symlinks resolved (/dev/mapper/vg-lv to /dev/dm-0); any other source as it
	is: realpath would read the SMB share //server/share as the path /server/share.

	>>> _real_device('//user@server/My Share'), _real_device('server:/export')
	('//user@server/My Share', 'server:/export')
	"""
	return os.path.realpath(source) if source.startswith('/dev/') else source

def parse_darwin_mount_line(line):
	"""Parse one macOS mount(8) output line, `SOURCE on MOUNTPOINT (OPTIONS)`, into (device, MountEntry). The source
	runs to the first " on /" (a mount point is absolute), the options are in the last parentheses, and the mount
	point is what lies between, so either may hold spaces, and the mount point " (".

	>>> dev, ent = parse_darwin_mount_line('/dev/disk3s1 on / (apfs, local, journaled)')
	>>> ent.MOUNTPOINT, ent.FSTYPE, ent.OPTIONS[1]
	('/', 'apfs', 'local')
	>>> parse_darwin_mount_line('//me@nas/My Share on /Volumes/My Share (smbfs, nodev, nosuid, mounted by me)')[0]
	'//me@nas/My Share'
	>>> parse_darwin_mount_line('/dev/disk4s1 on /Volumes/Backup (old) (msdos, local)')[1].MOUNTPOINT
	'/Volumes/Backup (old)'
	>>> parse_darwin_mount_line('//me@nas/Music on NAS on /Volumes/Music (smbfs, nodev)')[0]
	'//me@nas/Music on NAS'
	>>> parse_darwin_mount_line('not a mount line') is None
	True
	"""
	match = re.match(r"^(.+?)\s+on\s+(/.*)\s+\(([^()]*)\)$", line)
	if not match:
		return None
	device_name = _real_device(match.group(1))
	mount_point = match.group(2)
	options = [x.strip() for x in match.group(3).split(",") if x.strip()]
	fstype = options[0] if options else ""
	return device_name, MountEntry(mount_point, fstype, options)

def parseMount(timeout=0, unanswered=None):
	"""Map device -> [MountEntry]. timeout: seconds macOS's `mount` may go without output (0: no limit).
	unanswered: a dict that gets 'mount': macOS's `mount`'s return code when it did not answer in full (124: the
	timeout stopped it; 127: not found; any other: it failed). What it printed is still read."""
	mount_table = defaultdict(list)
	def add(parsed):
		# Skip autofs triggers: stat-ing them mounts the target (df skips them
		# too); the real filesystem shows up as its own entry once mounted.
		if parsed and parsed[1].FSTYPE != 'autofs':
			device_name, entry = parsed
			mount_table[device_name].append(entry)
	if IS_DARWIN:
		task = multiCMD.run_command(MOUNT_PATH, timeout=timeout, quiet=True, return_object=True)
		if task.returncode != 0 and unanswered is not None:
			unanswered['mount'] = task.returncode
		for line in task.stdout:
			add(parse_darwin_mount_line(line))
		return mount_table
	try:
		# As os.fsdecode reads a path: a mount point with bytes that are not UTF-8 (or not ASCII, Python 3.6 in the C
		# locale) reaches statvfs as the same bytes. 1.63 dropped them, and its statvfs failed (FSUSE% ERROR).
		with open(MOUNTINFO_PATH, 'r', encoding=sys.getfilesystemencoding(), errors='surrogateescape') as f:
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
	# Linux: the entries in /sys/class/block that have a device number (`dev`), as lsblk lists them: a hidden NVMe
	# multipath path node (nvme3c3n1) has none, no /dev node, and its namespace (nvme3n1) is the same disk.
	block_devices = []
	try:
		for entry in os.listdir("/sys/class/block"):
			if os.path.isfile(os.path.join("/sys/class/block", entry, "dev")):
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

def device_names(device):
	"""The names -D matches a pattern against: the device path, the /dev/mapper/ path of a device-mapper device, and
	each without its /dev(/mapper)/ prefix (the kernel name sda1 or dm-0, and the mapper name pve-root, which NAME
	shows). 1.65 matched only the paths.

	>>> device_names('/dev/sda1')
	['/dev/sda1', 'sda1']
	>>> device_names('server:/export')
	['server:/export']
	"""
	names = []
	for path in (device, get_mapper_path(device)):
		for name in (path, display_device_name(path, False)):
			if name not in names:
				names.append(name)
	return names

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
	"""Yield (read_Bps, write_Bps) samples for a block device, (None, None) for one that could not be read: macOS,
	which has no per-device throughput to read, a device gone from sysfs, an unreadable or short stat.

	The first sample read is a lifetime busy-time average: total bytes transferred
	divided by time spent doing I/O since boot (from the stat time fields).
	That gives an immediate non-zero estimate without waiting for a poll interval.

	Later samples are interval rates: delta bytes / wall-clock elapsed since the
	previous sample read (used by watch mode after the first refresh). A counter below
	the previous sample's was reset in between (see _interval_rate): None for that interval.
	"""
	if IS_DARWIN or not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield None, None
	rx_path = os.path.join(sysfs_block_path, "stat")
	previous = None  # (time, bytes read, bytes written) of the last sample read
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				# fields: https://www.kernel.org/doc/html/latest/block/stat.html
				# 2 - sectors read, 3 - time spent reading (ms), 6 - sectors written, 7 - time spent writing (ms)
				fields = [int(x) for x in f.read().split()[:8]]
			now = time.monotonic()
			bytes_read, bytes_written = fields[2] * STAT_SECTOR_BYTES, fields[6] * STAT_SECTOR_BYTES
			read_time, write_time = fields[3] / 1000.0, fields[7] / 1000.0
		except (OSError, ValueError, IndexError) as e:
			debug_exc('throughput', e)
			yield None, None
			continue
		if previous is None:
			read_throughput = int(bytes_read / read_time) if read_time > 0 else 0
			write_throughput = int(bytes_written / write_time) if write_time > 0 else 0
		else:
			elapsed_time = now - previous[0]
			read_throughput = _interval_rate(bytes_read - previous[1], elapsed_time)
			write_throughput = _interval_rate(bytes_written - previous[2], elapsed_time)
		previous = (now, bytes_read, bytes_written)
		yield read_throughput, write_throughput

def _interval_rate(delta_bytes, elapsed_time):
	"""Bytes per second over one interval, or None when the counter went back: it was reset in between (the device
	removed and added again under its name, a counter that wrapped), so what the interval moved is not known.

	>>> _interval_rate(2048, 2.0), _interval_rate(0, 2.0), _interval_rate(-512, 2.0)
	(1024, 0, None)
	"""
	if delta_bytes < 0:
		return None
	return int(delta_bytes / elapsed_time) if elapsed_time > 0 else 0

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

# What `smartctl -n standby` prints when it skips a spun-down drive instead of
# waking it: `Device is in <mode> mode, exit(2)`, where <mode> is SLEEP, STANDBY
# or STANDBY_Y (ATA), or for SCSI/SAS also LOW POWER, STANDBY BY TIMER, STANDBY
# BY COMMAND, STANDBY_Y BY TIMER or STANDBY_Y BY COMMAND (smartctl 7.5,
# scsiprint.cpp). IDLE modes are still spinning and are checked as usual.
SMART_STANDBY_RE = re.compile(r'device is in (sleep|standby|low power)[\w ]* mode')

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
	>>> parse_smart_health(['Device is in STANDBY BY TIMER mode, exit(2)'])
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
					debug=False,cut=None,unanswered=None):
	"""Rows of the table, header first. unanswered: a dict that gets, for each command that did not answer in full
	('diskutil', 'mount', 'lsblk'; see CUT_WHAT), its return code. `mount` (macOS) is always recorded, `diskutil` when a
	column it fills is collected, `lsblk` only when FSTYPE, UUID, MODEL or SERIAL is collected, or -F. 124 the timeout
	stopped it (or it was still running at the deadline), 127 not found, any other it failed. cut: a list that gets the
	name of each command the timeout stopped (as in 1.62; unanswered has them too).

	-F, -A and the size filters drop a row only on a value that was read: a SIZE diskutil or sysfs did not give is not
	a zero size, a blank FSTYPE whose source did not answer in full is not "no filesystem", and throughput not read
	(macOS has none to read) is not idle. Such a row stays, with SIZE, FSTYPE, READ or WRITE blank. A pattern is matched
	against what was read, so it can still drop a row whose value was not. A mount whose statvfs failed stays
	too, with SIZE blank and FSUSE% ERROR (one that hung: TIMEOUT)."""
	global _DEBUG_MODE
	if debug:
		_DEBUG_MODE = True
	# None (the default for library callers) means no limit, as 0 does; multiCMD takes only a number.
	timeout = timeout or 0
	if unanswered is None:
		unanswered = {}
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
		macos_info = get_macos_diskutil_info(timeout=timeout, unanswered=unanswered)
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
	mount_table = parseMount(timeout, unanswered=unanswered)
	target_devices = set(block_devices)
	if pseudo:
		target_devices.update(mount_table.keys())
	if filter_patterns and match_devname_only:
		pattern = compile_filter_pattern(filter_patterns)
		filtered_devices = set()
		for device in target_devices:
			match = any(pattern.search(name) for name in device_names(device))
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
	# Whether a blank FSTYPE of an unmounted device was read (its source answered in full: on Linux lsblk exited 0, on
	# macOS neither diskutil nor mount is in `unanswered`), so -F may drop it. On Linux that is one answer for all of
	# lsblk's output, not one per device it listed: what lsblk leaves out (RAM disks, empty devices, a device that just
	# went away) is not for -F to show.
	fstype_answered = IS_DARWIN and 'diskutil' not in unanswered and 'mount' not in unanswered
	if (not IS_DARWIN) and LSBLK_FIELDS.intersection(collect_fields):
		lsblk_result.thread.join(_remaining(deadline))
		# still running when the refresh's deadline came: as good as stopped at --timeout
		returncode = TIMEOUT_RETURNCODE if lsblk_result.thread.is_alive() else lsblk_result.returncode
		if returncode == 0:
			fstype_answered = True
			populate_lsblk_dicts(lsblk_result.stdout, collect_fields, uuid_dict, fstype_dict, label_dict, size_dict,
								model_dict=model_dict, serial_dict=serial_dict)
		elif LSBLK_NOTE_FIELDS.intersection(collect_fields):
			# SIZE and LABEL have sources of their own
			unanswered['lsblk'] = returncode
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
		device_properties = defaultdict(str)
		device_properties['NAME'] = display_device_name(get_mapper_path(device_name), full)
		# fstype, size, fsuse%, mountpoint, rtpt, wtpt, lable, uuid are partition specific
		# smart, model, serial, discard are device specific, and only for block devices
		# fstype, size, fsuse%, mountpoint does not require block device and can have multiple values per device
		has_node = is_block_device(device_name)
		listed = not IS_DARWIN and device_name in block_devices
		parent_name = get_partition_parent_name(device_name) if has_node or listed else None
		if has_node:
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
		# SMART is the whole disk's: a partition with no /dev node of its own reads its disk's when the disk's node is here
		if has_node or (parent_name and is_block_device(parent_name)):
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
		elif 'SMART' in output_fields_set and listed and has_sysfs_device(parent_name or device_name):
			# a hardware disk that sysfs lists but this system has no /dev node for, nor for its disk (a container that
			# sees the host's /sys): its SMART can't be read, and a blank would count as healthy
			device_properties['SMART'] = 'UNKNOWN'
		# -A drops a device only on throughput read as none (one not read, as on macOS, is not idle), and keeps a mount
		# of it that failed, below
		idle = False
		if device_name in tptDict:
			read_bps, write_bps = next(tptDict[device_name])
			idle = active_only and read_bps == 0 and write_bps == 0
			device_properties['READ'] = '' if read_bps is None else format_rate(read_bps, print_bytes, use_1024)
			device_properties['WRITE'] = '' if write_bps is None else format_rate(write_bps, print_bytes, use_1024)
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
				try:
					usage = get_statvfs_use_size(device_properties['MOUNTPOINT'], timeout=statvfs_wait)
					not_read = 'TIMEOUT'  # statvfs gave no answer in time
				except Exception as e:
					debug_exc('statvfs', e)
					usage, not_read = None, 'ERROR'  # statvfs answered with an error
				if usage is None:
					# A hung or failing mount: always show it, it's what you'd want to see (-A too). No size was read,
					# which is not a size of 0, so the row stays and FSUSE% says why it has no number.
					device_properties['SIZE'] = ''
					device_properties['FSUSE%'] = not_read
					output_list.append([device_properties[output_field] for output_field in output_fields])
					continue
				size_bytes, used_bytes, avail_bytes = usage
				if idle or (size_bytes == 0 and not show_zero_size_devices):
					continue
				device_properties['FSUSE%'] = df_use_percent(used_bytes, avail_bytes)
				device_properties['SIZE'] = format_size(size_bytes, print_bytes, use_1024)
				output_list.append([device_properties[output_field] for output_field in output_fields])
		elif not idle:
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
	if cut is not None:
		cut.extend(command for command, returncode in unanswered.items() if returncode == TIMEOUT_RETURNCODE)
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
	"""FSUSE% cell to an int percent, or None for '', N/A, TIMEOUT or ERROR.

	>>> _parse_percent('35%'), _parse_percent('N/A'), _parse_percent('TIMEOUT'), _parse_percent('ERROR')
	(35, None, None, None)
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
	mount that timed out. Otherwise SMART that couldn't be read, or a mount
	whose use statvfs failed to read (FSUSE% ERROR), is reported (status 3),
	since a blank result would hide that it wasn't checked.
	A check whose column is missing (excluded with -x) is skipped.

	>>> rows = [['NAME', 'FSUSE%', 'SMART'], ['sda1', '42%', 'OK'], ['sda2', '95%', 'OK'], ['sdb', '', 'UNKNOWN']]
	>>> check_rows(rows, 90)
	([['NAME', 'FSUSE%', 'SMART'], ['sda2', '95%', 'OK'], ['sdb', '', 'UNKNOWN']], 1)
	>>> check_rows([rows[0], rows[1], rows[3]], 90)
	([['NAME', 'FSUSE%', 'SMART'], ['sdb', '', 'UNKNOWN']], 3)
	>>> check_rows([rows[0], ['sda3', 'ERROR', 'OK']], 90)
	([['NAME', 'FSUSE%', 'SMART'], ['sda3', 'ERROR', 'OK']], 3)
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
		# statvfs failed on the mount: its use was not read (the disk's SMART above still counts)
		return CHECK_UNKNOWN if use_i is not None and row[use_i] == 'ERROR' else CHECK_OK
	statuses = [row_status(row) for row in rows[1:]]
	reported = [header] + [row for row, st in zip(rows[1:], statuses) if st != CHECK_OK]
	if CHECK_PROBLEM in statuses:
		return reported, CHECK_PROBLEM
	return reported, CHECK_UNKNOWN if CHECK_UNKNOWN in statuses else CHECK_OK

def nothing_to_check(table, filters):
	"""Why --check could judge nothing from `table` (get_drives_info's rows, header first; empty when no output field
	is valid), after the `filters` named on the command line: no checked column (-x leaves out both, which is also the
	only way to be left no valid output field), no data row, or no row with a value in a checked column (an unmounted
	loop, zram or device-mapper device has no FSUSE% and no SMART). The table decides, whatever the filters are or what
	their patterns match; the filters are named only to say why. A check of nothing is not a healthy one: each reason
	makes a run that looks healthy "could not tell" (3). A row with a checked value is judged, so a run with one has
	no reason here; one with none has no problem or unknown either (a blank SMART is healthy, a blank FSUSE% unread).

	>>> nothing_to_check([['NAME', 'SMART'], ['sda', 'OK']], ['-v'])
	[]
	>>> nothing_to_check([['NAME', 'SMART']], ['-v', 'a pattern'])
	['no row is left to judge after the filters (-v, a pattern)']
	>>> nothing_to_check([['NAME', 'SMART']], [])
	['no block device is listed or shown']
	>>> nothing_to_check([['NAME', 'MOUNTPOINT'], ['sda', '/']], [])
	['-x leaves out both FSUSE% and SMART; leave one in']
	>>> nothing_to_check([['NAME', 'FSUSE%', 'SMART'], ['loop0', '', ''], ['dm-0', '', '']], [])
	['no row holds a value in FSUSE% or SMART']
	>>> nothing_to_check([['NAME', 'FSUSE%', 'SMART'], ['loop0', '', ''], ['sda', '', 'OK']], [])
	[]
	"""
	header = table[0] if table else []
	checked = [field for field in CHECK_FIELDS if field in header]
	reasons = []
	if not checked:
		reasons.append("-x leaves out both FSUSE% and SMART; leave one in")
	if len(table) == 1:
		reasons.append(f"no row is left to judge after the filters ({', '.join(filters)})" if filters
			else "no block device is listed or shown")
	elif checked and not any(row[header.index(field)] for row in table[1:] for field in checked):
		reasons.append(f"no row holds a value in {' or '.join(checked)}")
	return reasons

def cut_note(command, timeout, returncode=TIMEOUT_RETURNCODE):
	"""The stderr line for a command that did not answer in full (see CUT_WHAT), by its return code: 124 stopped by
	--timeout (or still running at the deadline), 127 not found, any other failed.

	>>> cut_note('mount', 0.5)
	'mount was stopped by -t 0.5 before it finished: mounted filesystems may be missing, or listed with no MOUNTPOINT or FSUSE%. A larger -t gives it longer.'
	>>> cut_note('lsblk', 2, 127)[:53]
	'lsblk not found (it comes with util-linux): FSTYPE of'
	>>> cut_note('mount', 2, 1)
	'mount failed (exit 1): mounted filesystems may be missing, or listed with no MOUNTPOINT or FSUSE%.'
	"""
	if returncode == TIMEOUT_RETURNCODE:
		return f"{command} was stopped by -t {timeout:g} before it finished: {CUT_WHAT[command]}. A larger -t gives it longer."
	if returncode == NOT_FOUND_RETURNCODE:
		return f"{command} not found{NOT_FOUND_HINT.get(command, '')}: {CUT_WHAT[command]}."
	return f"{command} failed (exit {returncode}): {CUT_WHAT[command]}."

def rows_to_objects(rows):
	"""Turn get_drives_info(print_bytes=True) rows into one dict per row, with
	SIZE/READ/WRITE as integer bytes and FSUSE% as an integer percent (None
	when empty, N/A, TIMEOUT or ERROR).

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
		epilog="READ/WRITE: the first query shows each device's since-boot average (bytes / time spent on I/O, idle time left out), i.e. its typical work pattern, not a real-time rate; later watch refreshes show live rates (a device that /sys/class/block stops listing for one refresh starts over with its since-boot average when it returns).")
	parser.add_argument('-j','--json', help="Produce JSON output (list of rows, header first)", action="store_true")
	parser.add_argument('-J','--json_objects', help="Produce JSON output as a list of objects with numeric SIZE/READ/WRITE (bytes) and FSUSE%% (percent)", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (read/write activity since boot on the first query, during the last interval on later watch refreshes; a device that /sys/class/block stops listing for one refresh starts over with its since-boot average when it returns); rows with no throughput to read (macOS, -P) and mounts that fail (FSUSE%% ERROR or TIMEOUT) stay", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2; 0: no limit)", default=2, type=float)
	parser.add_argument('-w','--watch', metavar='SECONDS', type=float, default=None,
						help="Repeat output every SECONDS (watch mode). Equivalent to a trailing integer positional.")
	parser.add_argument('--check', help="Health check: print the rows that need attention, and exit 1 if one has a problem (SMART failing, FSUSE%% >= --max_use, hung mount), else 3 if one could not be checked (SMART unreadable, FSUSE%% ERROR), if nothing could be (-x leaves out FSUSE%% and SMART, or the filters leave no row, or no block device is listed, or no row holds a value in FSUSE%% or SMART: said on stderr), or if a command that can hide what is checked did not answer in full (named on stderr); when all is healthy, print nothing (-j: the header row, -J: []) and exit 0", action="store_true")
	parser.add_argument('--max_use', metavar='PCT', type=int, default=90, help="FSUSE%% at or above which --check reports a filesystem (default: 90)")
	parser.add_argument('--sudo', help="Run commands as root with sudo. Needed for querying SMART info.", action="store_true")
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('--show_squashfs', help="Show squashfs images on loop devices (snaps, AppImages), hidden by default", action="store_true")
	parser.add_argument('--show_empty_columns', help="Keep table columns that are empty for every row (hidden by default unless named in -o)", action="store_true")
	parser.add_argument('-D','--match_devname_only', help="Match the patterns against the device's names only, not the other cells: its path, its kernel name and the name NAME shows (/dev/sda1 and sda1; /dev/dm-0, dm-0, /dev/mapper/pve-root and pve-root)", action="store_true")
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
	# -o takes "all" in any case, as it takes the column names (1.64 read "ALL" as an unknown column).
	if args.output.strip().lower() == "all":
		args.output = "all"
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
	# A terminal is redrawn in place (one write, so no flicker); piped output and JSON keep every refresh.
	redraw = print_period > 0 and sys.stdout.isatty() and not (args.json or args.json_objects)
	# A note is said again under each redrawn table only where the redraw wipes it, with stderr on a terminal too (taken
	# to be that one); anywhere else (a log, a pipe) it is said once per run.
	renote = redraw and sys.stderr is not None and sys.stderr.isatty()
	check_status = CHECK_OK
	nothing = []  # --check: why it could judge nothing (nothing_to_check)
	# The filters in use, to say why no row was left (get_drives_info drops rows by them; -D alone drops none)
	filters = [name for name, used in (('-v', args.invert_match),
		('a -D pattern' if args.match_devname_only else 'a pattern', bool(args.filter_patterns)),
		('-M', args.mounted_only), ('-F', args.formated_only), ('-A', args.active_only)) if used]
	told = set()  # the commands whose note was printed
	# --check: the checked columns a command that did not answer in full (stopped by --timeout, not found or failed) can
	# hide. A filter drops a row only on a value that was read (get_drives_info), so such a command hides a check only
	# where its answer is the check's input: mount lists the mounted filesystems (their FSUSE%, and with -M the rows),
	# and a pattern (not -D) matches any cell it fills.
	patterns = bool(args.filter_patterns) and not args.match_devname_only
	def cut_hides(command):
		if patterns or (command == 'mount' and args.mounted_only):
			return set(CHECK_FIELDS)
		return {'FSUSE%'} if command == 'mount' else set()
	try:
		while True:
			unanswered = {}
			results = get_drives_info(print_bytes = args.bytes or args.json_objects, use_1024 = not args.si, 
								mounted_only=args.mounted_only, best_only=args.best_only, 
								formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
								show_squashfs=args.show_squashfs,
								pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,
								output=args.output,exclude=args.exclude,
								filter_patterns=args.filter_patterns,invert_match=args.invert_match,match_devname_only=args.match_devname_only,
								timeout=args.timeout,debug=args.debug,unanswered=unanswered,
								)
			if args.check:
				read = results  # the table the check judges: results is reduced to the rows to report
				results, check_status = check_rows(results, args.max_use)
				nothing = nothing_to_check(read, filters)
				if check_status == CHECK_OK:
					# A run that could judge nothing, or a command that can hide what --check reads, makes the run unknown;
					# any other command stays quiet on exit 0.
					if nothing or any(cut_hides(command).intersection(read[0] if read else []) for command in unanswered):
						check_status = CHECK_UNKNOWN
					else:
						unanswered = {}
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
			if sys.stderr is not None:
				for reason in nothing:
					print(f"Nothing was checked: {reason}.", file=sys.stderr, flush=True)
				for command, returncode in unanswered.items():
					if command not in told:
						print(cut_note(command, args.timeout, returncode), file=sys.stderr, flush=True)
						if not renote:
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