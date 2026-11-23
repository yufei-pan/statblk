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
	if tuple(int(x) for x in multiCMD.version.split('.')) < (1, 69):
		raise ImportError('multiCMD too old')
except Exception:
	import sys,types,base64,zlib   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
GhUEUqgR:#dNJ=oq$R!0UAiR@7$&a\`(>T9o/X7BBOY1PbO-=g_,)C*@8%8LK!_U[1r%_em-GDXhtnbt!rEVZ:U5+)2ZTZ7,W#&b`?KhRWDf]iSN:oYo
"33hDT^MIZ[D9s>C>q+fB\?(nO4tC>SaBJQ`_uBfm"Ep=6IcsWm%4-3r>;JUId24B9RIE/5#e`GC2<*ZIN\e6ok0`SZUI30e]<FnbOFZb%R&/AVPo6nm
\2=KRYrHHleRKq-jb^emnKZ?KI+:W8*mp=2cF8bG`'+,6e67XRjUd>-Gr0ltee0hjU[)95h@o3bqN!?I"ECFP-GOX\&RCnb_-4J+-ZV.PK4,O^G5'a"L
d@]hP+`I=%@V#JGa[SUS=pd)3`$c!g_P#m/8Fbgo&cmq;G?0/'W1ra67dRf.)e@Bk<+I.Sn:q=H?)O&'-]OMD.5Wq1Tm.inq&7":$,$&b'MrA9JJ(aTK
9n+WOt2"]UnVpBfQI%.kGF0`s"PN$VNca1DO4WOaEIt)c*)RVs-f8#Mb?bD-=hRuT"KAC6jT!->G4H7NUSu;0r%<GE>iUl@0T9Ga9S9odk+HIjX^@8GI
jt^/W1^CV2n@"UrHZaT(m-3iRkNT>5(WW_Zn-%W4rp1?u'?1$pah-`Vl0G6cInY*9]2ogEj<F*:c*W#ImnO?k/<YBFSsNS14ZZ/A+.jPO3@W,=@XORiM
8(Uar$0G&O&+`hS)\.:-R\-hDiW_gY+bCmiMmFK5CE.EoT)f*,_#U\h2Aa4cX&f5=4#**WgY".q=%OmVhbJ&Lf-ZefB"G<[dk1TTHN`"Ndc5$o_QpqnC
O;I5P_?%`i"aDF[#CL`oVHY?3R@o,)kVrQi@3Oft('Jp!\WGdc]N&#Yu8dIi!oUH(Ie6SEnYCQpq<RmDJ2J+p!Q2`l!E@HoOd/3"fJ8&bY)t5dDfhhHA
'0;I#JQs55E`oOM9m=`D2Gc][A55Od2?'K?)l^ha$ro]g;g=^jaGoY[`p(u=`lj#^PIG=u6jpineOhqM.^WkNh"r9U>[g0P%:9Tnr8Mp^eK6h76ZA2K8
8YWqt8nN/jpp$/"FSut:'dsSG2Gi6BVnl;q3SlH'To;Vb853eHW3FM-r:OKr&'#'^mS?Kqjo.4:>pIAX_6c_GdZK4.B.D%cKXbp-Na74P@dEbX8`X+0I
;dan,Wtk-9^q\[Kf/`I@6`[^Z@*)uO^iYtFQbk@>?_*c@r6HbL!#q$1HN\alZ^LPBQt^=4i8pejj-P&:5%]uh_(5Z;`$9l]HCq/Id0FCN>W%5F>%R$EC
>fK\!KFrdpmYS*e*QhBUAo?Hrf\Vs$\.e""<=&`a"ORB)EqH*\H%`iLHZo(&q:<:$t8/@N+\3pbFlTD+[fLe=[B4L;lu<Yqro"22PkQ,f3W%3<DXg5SL
n8G$/9gZg<shT$(iS!VuVqfmEU5N_9[6.pkSUZ%YHG:D?L&%#=b&FPOUF"_bb$aO*rn!dq%`0ms`mOk?0QW:U%kg$t`[Lj_J7>&,hUeS[RL$Hbr3m$iB
^+`":4qH5>"Z&$W_sf&%:5`KZJn:J[VG/(daWe[6NH3A*t6U*k$ANCtp_=31g.,]p0.3P[u-[DmiO859+6itl-WZddJQ2HHUA!,;^@kfIR5E&I4MnUo=
%Z7ZLcRI1?,$,a34A07h+L$l^q`ptll!)5'm=cc'0\-9^]7eU$MgUDZ(JQ9@/qVid20s'F&gS7i4rHS8.(>584@0BE\a`0M/OMb(%JqP@p9Dp?K8$poH
/1dc@Ge_,Ur!:L+p9%$U0%`eZq1gLiJYu1Z@(2]D,bjos&$KEGIsUtRe_tSW@j9q%.mHek5TS]cBJ+0c^f@#DcBtfa1]UZo#3+=tj`iKh@smRa;^-\ro
TIf]/f>QU^P$;S2X=m5dZ6)EqN8hW'JGa\OEqtOegX4,<ZtR%eQ41b^J:K#-$3b4#!$H]ci9S2m7,RdqV$3Ag2c)lL7oYQ_Le`#`9!6/5^!N%Gr&b?;O
s+3$QA#DUp194P@-8,YOcQoohbPp!ai1r7lHCF..@[XjdUOHT,G]?M'(e9%*ZA=LG2\(+:H[q#T'*"mHl%t"DW7$6jO8BJ8V-J2:XW#J3I2RGFA,igOO
gohiS?4h[r?S%V0OR.0A33!B(*CE.]Y(WZBg0l&1KW0@MX.$b*W7I)tqW"sV%t_m@+#F_tgZ?X[@pi@&`k%8So*hLbYR%C[B@!$5"2=hUN%Li-.ohN&N
qW,)R58p)W.aVoTIo>!KZOLPb8&N28r2,#BfH]#4M*s.ZsLgQ<j?EOD,)%O1+4Q@T)JIi#Sn(k[>?4H&m+tJl9Cel0'^"F6ImaMV^.]qKP`QYrf>.7qQ
#A`9!m`5)7[q&DM_0^_"-F5k])m1Ma$f5+[FZ]/3d_BXVFd<A#')[JFpBJ\H&t:,AfHM%<Z$dH&IZ3f647Qh,Dr\1h)MI;8'':=P#HUa>@,?O?X&09%\
DR7G7D>E=-.!RV9_p!8k1A;O11)uc7[[PBQP[Uj'/lk_'E(R(!uWbm;)pi(!Zt.Kqlo813MtL_i,,'F6%TUP[\Tb8I?#T*!2q_1Rubl9??S2TT-a=Fh0
i-ohJ:u'hn%jih_lU!ka0`r'R(\-*-(#?01P;dMjWsj<!eSoX%bL^7*6q'rZd4V\0Ua1diICM#T=S5p`0'Af7&B16D.W^)dAD=`,MVUj*WF/"r:AcRg=
R!L!^N%')CR6i"D:i!AD'O"`TW6O\^S5/Z#*@34I0hi\>a97-5Ua/sC1F"@;:iD%g:e])>0Jlr<jY`/G-g:3qpSXZk:u"q__]Q#I*p'JI=TXn:]Adl22
2E]AB7oNO^4b`MBaHBHHl@>Jr:$?/MZ!"a&s)&Z=tbP[U)8d4EM7&B@FA'N%rC?0Qf6Gukp48Je8`br@=HjLO/gHi6RD%(CfdM-GjE8N#A-rXDUj]jXI
CZ%G)FI^/m&4$Yo;_.VR59bmi/M=^JQMD40'@7<g;FJRXYkJZ*#@Y/"T)oN/i"0`0Fp[`0'ELIuJ6kVF4h$9SB['&c1SnK:L8,%9&XjsD"B+k10b&LT:
dFM40=!+)^'gr>++]fqBXK30cJ@H0VMS=g_U:9gZ&g@m'q5OGaUs6U;2"JW4iD_-iJ1i;,cfJ8g5Br]$75HJ)c@BGk=E\X/ieJQSWP`o2,HolbF'9c2/
S!ORdKrndtZ8oA+WBIih+m];445+Wki,>LL8<$6kNs!6o-"DXcDPsCooeP_R7B*KALLCKp;#h2IgKg=<[[DZU&sXp$L"k[pOB^q7ms5&dYK0!$oL.YqF
K^nP`c-IcRE:G2Y*7%NbkBp_,@Khp!Yc]9KcKn`)R/gf=V%h0gbWfX;Otg%I=^#U"3cYfSqK<^gLQ?7XURJpfG`hdkR,ea_O8d5X!XRl1E>(?4IND7mB
EJVZc:]-%tk:'h=(<D(lN'1-MRRh)%&R!P-)A<Z`pUAOY9(pfGF_MDdHUOamSE&02g$=]*82@CKM*u+XpG_)t?6</5B)>"B]QR]!=U"@cb]Nib&f/j,R
3=(.>jM=hS?&c&-BCj?5+NH$j1DX)gj.k]u[u6C"ff?@U$g1W?2-s'2=J*IWZ!N7n"nj\uG<U_<p.7&$Wsa>0_tN>Gb12Pc\41EjU:!=!7$C'1i>:2,h
>rgm;p$8S<ET-ne:h)b_[T#JqOeQd52EF;K3Adk.[gO@7c`U;<=/7"aG3?UA:CK,Q)Y7NLXO[g^*t_:Xggq?97iLHb)RZ?aqD7]M]uF=UCG^%7V7SC*]
egC;WIi[AL7eQ*b^!Xej`i,J_2ok2A8gg_GeW=RUERJj'PP6VnSS>S9>4@1&#Tr:Iq$+_HBm`C2cP"^^1]G^@_2:LiY_5PPm7H4UfCVYU#+FT"rU<Z\V
pYc1fc(n-E\U&*-*FLK+BZ,5PX`aV:SXI&3c$6H*l#Rbr32RO>tnEg=o?NtJK)/<`n?G_gmESmHLq9hQm5P%'8Cdm;9Dn(bVh7+<tfCQe=GjZ4M%->Z_
"9W]fGgco*?D2,/eYdLap2LK8W[u^KoiD2Yn#SEf[*&"e(K9.G"B0p.?W3j.gdOLGuKoak7CLS[:8QFo/`<>I+BnS+FZ5fK@]V7;mT/74&eF*.$*Z^?0
11?E"ZXS6O(q"oNBMq2_%s4_ene?%V>kN-$JD0G<)&RPN`\uTDn^CUC5%_"]R?7q._eO"mPtlU#8CZc5aS'=f"gtol>_KU]nD1*hT.OC49BJ7^ZXU2tC
[X2"5fA&IGq6iKD058<ZIC5Y&L7\]koLnZqW$$@o[OKt#RJUI6!A[e7o^kF!/L!65W@RBI=I2W6o2F610[9cYCRHX&F)nAI?"c.!cu]62JX2b?2%X,oZ
c@DkD+!(s7IBPY4^qmQ4<iZitj?Yhn8KS?MJTj[iaM@`c!sfg(%\-JKQ')V664d`FUcrqs%!T7tkEg]Xr3\0%PSZS_aB9SEJuPVRZ^POZabfE2%Xe,u[
A2[nZ8jWJCn,Gt!Kc01!3.9s8k5*RqI+%4CE$Nfu:M-%e%s5/:ZbN7@6J;:,d%-HY@uD\"q4J=8GC>kt<(Z<3EoS5c72KdOP.6qOD]&b+IBUBkX2bNm.
.n7+B0XG^)RiWG3Pg=W3>1m(A=gXW$@07lYLjq?'`FcE:(frrJ77t-eDA=ops`6%(K;ToN_EK0T*9;HH",52]rZE@!IiP^K!qQ493!?,Ph^lHY^bf$*O
GC`aW<6[?M>R-QQ>[L,153+B3ACSu@Elo$ua^9M=GbT]L#)eR3s%3U;)#k1nQgdKE8f>Dcr-n^f@^IG%I"3"6^'*-ZK--fBP%L%_R^>qS>tSNEb,V(_"
:)Ks$Fhs`:G)O1RM.f5U\U3sr.Z!fi::&Cp?jb8(%oSK89Zf\%ES8*2H0sFBbsn%F.du\SSlL,!bagQA5+s\nf?="Y#p+c.IS!ch;"Ir6*eCC[(g@eY`
ffj'+Zo9*4rE)SCM<eVVH/oDf-dek3<.E4i94`-[Y/YG@*ZcVWJg"+2/DW^9K+,hD8<l(_VUJMR%/:3f!H'gc'u7Do5kIEojkE8$H2s93/3R<6;J@Qrf
4*41B%f@a;rI,It^]V7?r,].\plK[.!n"H+3"M:D=1C@k(oNoQr7Fm04@MBsaM!rHeY[$YGIq+R^t4'"Eo)H$a8EZr9P"VDYRC&l!@(X\iCdOMjOm2b>
\PCLR&>Pe\ck)f%#//A]+e+Jh&NpJfr`Efki!2c3"M7P`P*)-UaQ=QHLZ]D/lA:>).>Pi'[q0T8u6c[GID0`eQWP+<f!n!mha@*gYgRZXqEgIt"$AMI9
nsJ6;l+C!c=P!WdoS&6-RGGS5RFHm-XDS-@g:&pp.^iKA?`prVUfa_i"eX'^3:m-bf)EeVO94]N"n@af_Ri^_*sjH[FkI(BGStBbWOjcf%.jFU@bOLI6
::o[nL<L_AQ62idMT"AkJt^J_eGPi3+s;-GaUglj2'"67#/S@3)g^8ipgolgV##q;=;*OW7(&Ko!GS[**'%J-?<G$Y.,gJeI$t*/].),$8i&fGN5N0]i
/Z;&#DI:+2V[I$1O;@s7i(/55kVBnR%GmkSoF8ple,`H3l),s!%9d?VQL7S8A5pTQEH]Z3$j`"er\+EB+D7.;KHf\s%.T)O-KK!LfR>9?:M;N#K:@o5Q
cWKTorAR!hfSVa`F9gq?oa+R2oD((@U0.(p0a<B#kD95NZUKPW*TLc8e=1pansD(%l^`!u9gQLOA_:5TYajdRR=;$fC2Y3`&__NUt(,'3&UH7e8Ta)l*
(daCW!mNasMjRXh&\MDM7C<=ea,ru\sBk`q71'4WH=,W16NRfE#`Z6E0cR#bB8`*cbTl=J#+H60^&ke3Q1O:433;kP&kL8si583nq-7k)+51k7KoEX"U
cQ]UOZC$-'a+4/K9Z:tDFs^K+*WflJ",DU%D3<g7R5/Wc?3pG[>Ahn*bNd6-B\)S^BLA::_r-R"1aQHM:c%K$l3Y'FA=5_PHMF2j(.=XKH\8BDZt<`W*
Sf03[JeoF.B)\D\_^nWr*V6jlUFLBMCLC+[=uNBQ2Wk3)a(/nCt2S`WnW'9#FaYG2/1WJ\96+@D1\i<)]Mu]_nfNig%K/KcDL'ajg.f6]CiZ"^"/8rTm
#U2BIQ;Z(q&bUg"lY0D/T&QW3[c\jjto\-lSg3lAs$74[^$mK?Gu`hmmhgVk\0d/6,%_>)#i6XkM^-fk)_>Y^Sh6.F`A-X2hpN(b-@7!/Z\'#3h;Q)+E
^EfQ-$;gj%irO@JheT\td1JrT*??=Oa`*7S/n%HAruHTK(s7k2iu!cC!IHVHHEb,!\TP)XH2,LKG@#>@1+0Gg].Zr"c\Kt+I9g$<@@*-B@UPVik`02Cb
:CE3G*\a>44@l4l1L*^,gRag-Vb?NJC1Bmi7A4D0,YWgbp\]<n@*)@2Ie2kZDe!hZOqmopAdSVQbX;H,DP%1=BE%I?\'Xp2U'?jplggVJ$/Z=Z:6h=oN
1RFg8NM\qnrTGOYGs5P<:X0PN?e;i7<7u[3`g,-"BjD+]Xk5gA6YeUYY_bCbO%h@d-[hj5[#I2m?<(!`AkD(7NG)R5YtS1r"!=kWF+JH<FjBt$oa>Vpq
@5dH6Yc5W=DXO>GI[=gpGlPQa$`+95AfaEKW4@\@@$=^5G_rL'm$3#gJdjQ$@ZK$c1WLm=Hc(Tp[:FB_26fTK!E;)DU<gC32)8+piNcrpR.U#\"nULEZ
2_(-fc?\j/m<"1%B277S\1A"Cgt7^6V,@>pVkO_j,WP%nNog`/7>0:tes"?8J_APrqc4^%V.<#"G\X,&0_?of9*KcF0Ug5TJ&l)a&`1h^li4/m$F*O:k
ILY944grtgkmY8TJ!/OdYnQa@^(9Kq[REE'RC[C/gaNBL/9_g^D*O.r+Jm`=*Jc0hRr5k,W=S-=rL9%D%OO2/bbn=%n#Pj?d`i>4bI0(Wl\C`!,:h>p5
p9^#jU+j9Cp`+BYlY/kY>:8L=p#bHIsFs'?dBLUA`1;LPu9>c.CUGZLS4V$#o;,TbGJ*N(/(gXD^5UYpNO3h+8@<S"h#ATI-LJtC;+T!0$G?ui:(/S\X
OHTQ/YZ-#qh(1]h%Q,*hS6T3iFss7Yo`#D9UYth_^#8rqD(Gl5<2#U<G6#q0S"'r[TT"..0?;Opm5u3?8JpD^1^-ao+3sRto!ilG7;o*5HOW0J;A"Cf`
HE=L,i(VL2'2(T^u2q,.nr+-&+`Yp,?&hXc&O"6%5^&EG,m[@^Z5,PR*]kbJ,5)i,<OQ,>*^gT'8#_oRjAti.jL?O6Q),a-@j,+I!IG9RtSGM8jqh9^a
M9=jj@n*nTs6q)(f!i%5qPgkhkf^gMe2++),iWD]Use5f3r5Q=eZ.KM#Y!#0lJtbt-Eu_et3"EZYRa%g\@K\W,-YGq9Yi*0*=;JMYOfUt?YF(LiFc>.^
#&JjLhpoho_eVAQnPPhA'CA<YNL/BXd/(7ge.Q2oEGJhM43@[PTo+n_c,)_.j_pJ7HA=LG+b^I'J8`(s.ed>1ap(I^O0`"WXW/iRFq1D`2]'d+Ul[9ms
mr;-M)+e-3cGl`Z`n53l8?pdNADN.c0<QZ'NX"8WI;]Ch2a&7^LL(lk*#,)KYL[ckJF`"aHV;X'I[uM<R?*9(LAjR9Xga8,548h_Q271dJ:J]iEIl`&M
r$:NNNU[?^Eb=@TJH%%pE)M>=N;iUnY2p",,K$Pp1)G%,!Zbc9XV@spR)TgT:&:"r[\HM[rQTZ>q8R'jatdZb%^f$S#QeF3%NI26Li2SCR*:U`\ONHL7
^G\h1_Lt$6!>%c]>j'%TS7B^;6<Tqi]q^bC:51VSS1&"T3nF&4hG%<fj]ZtB`f&?oCZ:VieYa`iAPn#Z!"_8G]"s$7R).ieQ6*?ZEJ3ff629\aJq.3a0
E0q<!Rk06L)O;k98R9bLOM-<S(WVaWbKc_'CDo>==Ze@1$kZmOLd.qbp!74gC;CV.6r3MX:YVMFl0ZZ(.LN.3C,E+4Ml8B(SCpfKf$t4U=\#lc1d6D6D
f'E[jA6.%q'6rk,Ai2c'icV@r.Z%Q3XlZui9<`)]UFYRS$?bB?H4UN-^-lFPCTE,BDeqGnOX;31!*\hrd_ST^Yl$'S/RHbrKjDUm_;A,ODU/@$eSbV@7
[F(1)<GR%>2J=%;dH'Q]+q2Eao1dGN+P^_CTm7ZoQqY"$>?k&0CdVEJMIGCmI-*qp`g:lN%8m6P0kUjLL]'-]u!?+scmD'/cJqksuN,%t'1Ku#S>-6NF
-jt9HL9"QMQ"k3b!BagY/^o<V3G@Dr8-!=ih3SRqkD7rSe/0b&'D?VmNl[oE)UEN()l?mR'e/H8Y-0Hc"(Kpo]l;H,<ITD%L/"Cq8a;G<gNn!]d*iJok
&mnccD*1t9#gp>h=>J,q/d/Hn;$tmrr,3qqpdW4n"8(4IfIUi1\_,-XqK4\P:-<!^H_MYX22@<nf)n!B"d4@#,XF(,S4-*P$WMGBW!7OJNLr]42C@EJ_
&dgPt:pRC%I0c0.nX4H'Yrn+.Af(!\@LA;n;*srgrXe3FSE:O'NmmN6!#!n*;"P;$,)X8Om3b?CY)(8Cu#1YD0q!&7?<80(PgmMa5u/%:!Yn)[Bhmqd>
rto:gYq"#AE\GM6u=pCW)(.ZD['n+/4o;npYq>4;&,=e"LY5gY];'tU[h<"IKQH9doqe>Z8t!G@!aBMcQac>.=uSsBXKHr6stP]=A!oAXRKpJdZhJNW8
&B\GLN<JoUoBNf25cZB/TU5XKpSSdqs+3himB@CkU&(*5F=/dd9UO+ehR=VW_d<<d.^ha/#$jVR:LD;&qNO-Ho3DcO;jl_O'O1ug9GIq-F*)sKbs"cL!
I$;gJhGh$9KlN0MEHhf<jD)no?,[mjpAhK=YJksc:M`Ei_1U+=#u<S8X&g7p?N[TGX5`RcCl#qHfjGbDmGn<oYZ6Og\>[&B?R4hd@"kIm18Et#<"b`oV
T0$275:b)Y7lWt"&t+:"D.,.ba&;;RbjqZm;ApT-mAeP]iL;fnh//6nBe6a5.dS7J;(tu"ihbQo>(dK%B8IqRXe2<D884R$&I3BWfi\S90gj=,?_)fi@
DT28:s\s#)p^dphCCKXL^rmi`NC!)i_bV-RtugUtfXQ/BCi@)Jfmp4=6,';B_@Bfm&c./ucW7!3)P&8\$!J3RS13%9-m&])h@XZ3Z6aOmA'2&#:KVL0)
ENYMM_SKF4YhIg@Wj>7eoA(BRUaa"ggsM0ui;]c+3qVt.=MS7^OO`rNL>3-=ZGd1:g0B2(==pQC)j,G$ejXSO/"KKCD?`"M)jC)<W30!MFD>@5/Q")nB
l%&XngT9oQ?'uger+iBMoc>sm#^5Ul=5JIb1D>J3!Q;"bGU@?$2Z]^t`8;0Wp,R:\#;+'FdJ'C;S[^$SsUMe:,/u=W7<1ofSIhaORZmXMJYGTS@%)qW;
rjJUP+Y#B#6P+!:\VhpU!qq>QRT"B`W\j[DEYSsEl)$qJdU2+D.P;Q9:Gk8BRY^jTF_S1lJ=jf9Ch4U\<m_ZL=nFhD(K[C6A_LHR:(BP#]2JK\($rG4G
e.#^W.;a5ECNh5'T-mWU[u`HC'6S2SpOcZd"J-!CBGd2W]H82$9n8d,\MS`O7r>*?Vr'P\rKs+EaLG6-jg.$eK!Tu.Tme^J9EjDE^Y+)p]WRfE59-qIC
1d,;6o%0@8#_n/:-N@(c<LRX4e0M@:>!>-=Clg[2H=m_a*Uo==D%9!;U^E+fJe:7@&S;!m)o]fj[OM<5FSWJIji<@:n0TQ!j!?!3tr(F\=$P:5p=h9n-
\c=mboP+M!,/2$tZGj.al3";OC<Ee=u#nqA/i8:Q*`a&h_9]SKN\^KAG^OC3OBJ3j0ABYSoKZ41g6"tD<M\>6uC?on'\e]_[)BHE*WVNRB)H`o(36S38
3OTe'd.VF0+PBH-F%"JqQ;@<Iu:C\XMae(,"@?\_;U<8.W-\b;rEkE/22dV?6n31YueD@Y4N\6NIpX'5S2Z:u+Ek<lTE249b@XH&PJ^\Wo?BuDHg(O2,
C7][D>?+f0"a7@)ehdT_%WXNKP')a$^[c<`qGkNKi[VkY@l;!KPP6b[S;:]X&RbO^OUqJ^i'.l>Z6NLBe.bL8UGgeH@1/csX%.3[F''GYSjX[&"NtI($
)t%0UeN)QI%!qq<#s`H$LKBqSRK`TBWHekeIL=P+cC2Sj.^A4CPRRD'#*WeDJ]"/)lM,$KMeq@AT*?d=u$NW?<B0?/CrP)oZ?(HQVUD+MA3]=kIYBs7O
I:fBrH9l)olhrTXE=-_[:>BL1Jfm@]RA"Ot!NF??=u_B3uPM:iu^i2,"%'!DalpAAJfBS0m6HfY^mt*hdXQDsn#LfeRbgp6"1Ef$MESg0ZQN%d)9jm.@
;[!OEmES_P<pL\<E6HT1D3PFE)1WNLJ@3k7LW#^"fI^bl4W`M_JFG^eCbm_.FK"]j00*@Dd9`Rn-O\HbrT1oCO>dPNl:6Tj/fl(bDu>OMd$Fh>]#e/4H
,Rcg$AP90A'`^8K]XtgF7T1s0,0Mg^L]j02tfJ3KF/V0diDFhb-Ksq90@ae9M(<Acjd-'GBT^]n,Fcd,CHI;OteFla8V<QGFJg:!o5!*'3;`Lo32V'/B
J`uM45Mr)n4?-A^)*UP.:EPUZdPCP3F6t$+7JJpS,oT?F^J6BJ+$BDbb:gX*lK^t=htJ4@rUnbIrNET&)=,WBrg2R[h[Bu!2lk]LbrP_%m.PHQii"HB9
4-LmmrU\NAZX[I%&)E>\NFVbj/C[sBH55pe,hFq-qgMBNl`@.N?9Xc,iAeuSEDp%'J%K%&H;nO#MtAJE8f:XaB;E;5Shns:0(kHqa^UhUT/#)J7[ri0e
TtFQm-mKkH9'1Y*3:)n+6@&Gol1,"(No6*;)1I3A69LrFX0S_/u+9?jkKV$:0iJiQ1s,J!LbP\W:1h8XVj`%(9unm?t&"fkMF!ch,mEJfS\c!U@TB2$W
GY.ol+Dj=;GE-eRQ-0UQGhU8H]2otIG@3fq)g*n&DO+JmL%1a$%;2f.59\\_Q^QP*YRX22A&ZB0YI6!>.,]G@/IqZi69*Hc_5Pc;cFSn1PI+_5kY<!uW
//.@[k-7@Qg=rXIg?L'(da26J<Y!Hp%.>l4r>As?eL#nb.:/`Y-LN+W1QUu:M#K[p-Uq@H*XDEIX].hg@fCqmU4G/=s>7:d!597F^iRbs;qadPLLdAfl
"e=oqk>7a4ON:Om:kqJu1QKHrRAm,er"W226L8-TT#-eAb=p!bmTeQ=dP%:Wm@R,1eu3dqi'G0KL3AoHm^TuaqOt34hZh%P0FSq[@CbW?KOHeNgIX?ZN
hdS#f66!dSJ,p_C/pY14iPd"[C!NYIeY?D=m7(>hn2A9IG=L/a0.1UD'LY;(fC?0![-9$*H))`jcqDKIFJ81DLDcb\;Uh:)^ojblBI\IC<l61A[qSMnR
2Y&Jll0eMp#]o*0*BXSfo1PF]s^gkJ=Tlm7nE@&`1%,Cp]1BQqe2jcE9/@OqX'OjiaTm%4(+hB4>j=q<&-Hh%G7<`D1.t<QF'jO5;p;\%<F9;AmHLhnZ
fQ<Y,a_C(Jb)Cu6qI4fR78K@B&_oN41>3=?*NX4@@Ud<M%hH`s%(S[?+Zre3G51H]k=C-C4lKEW:]P(f0jM=nTi'=KlASV`!M3%:OO<%B>5CSjc`(;9F
76p:BL:#X*tLK^jXRFk:(;NI;]-'Z86dj=h`A/VV9Z,aI(V`'FF9o8J%>11h0S)W(p?A!t8_ol(&@((F:7V65P_-Y0YLD;OYhI`>g0#rdaW18o5^_tsU
k[G&q>O`8,a`L35;RtrcA6dbRLYN/EO+7N>1:YGD6O+'IQ;`pV^U=A+Rk3-XG]:'YX<ZGsMfO>;"D&cQh=X1j(#X=(r]KP.I\6Nc<TY-1ipFP2..%qQh
<s$1-Vn(is!aZH:uO7g>V=04<Ete+6nf?9@@j3a?P!_-K@,2Lm,l8t4g2;;FStLd:IhT`r[RD]QftU>rs8YpWDU%P$Da#KRe,a9(Ijd1Y":Y78G2[->J
U[BgeTHJP3n*mE,M:sf'.Ub=@fbtOuGkVoC8+76l('rCLgtHRYg>DWM#]C7r6H0FTtJ"hP+@>#!U\#c1?C)^k9(D@&n16^G^DMb@Z6P>)@eNO,@4`.:7
`Sptl\^H>?OgdF=/pD(jmNL<fTi[NOVE.qQSE9KB,5\2Z""W1l6oo+N.EIN<F45,/.m.adI:-\4e`nrltNES=Rq[!U6#bdNnt^T"+gCHp<[a5qQV`&"B
8d@j?+Zp3$i.t[FX]4N^K;V+fFB.@[?$;0'.:1C6US;qjt"X7Ym#erm'FlTZ'._6UTlAMRdi^8SU$0#?7FYR4S<RNbf,BbMNM0TaQ%t']<Mm\U"fBNNM
;iB8oYK,se(]!qZXSPH8V2r-$YTo;K_V8i4Kr`3YQfRupl=LXn>OQT2Y._.MFt%t6L&qjS9W%k1SUMfET^gZB9*+,27YL)s2)Hfp^c<G$VWmK>%etL_p
i)ti]982`qpN]aSR)="X0Ea(`>ccL.MNm%:@K?*&G@QC,uk`C[?<QN$e'4T0*ief^K5qO[q%k97c-MLkGo.'Joo8YW]Js0Z>)UIjf"jo8[M5%SZtk>Ag
Ii#$N[[)E45-&SUBh[\/`nkN%3B;f[hndW91S7G6:,T-oOAkh?r9ok@'bkFZ2^+V+lJt.6&UJ!&)pNSW7S1@*LKqidkJR%l-@`d6Yai/:),%JK)4om9+
cR19=sHT76/"d!8Y5'DXe5<`qNtKUAFXJa"@c:u!G-/+3[Gq.t2S\tjm;f9BadB-rsE0&f?'@:?1BTsQl7CBqQi?lRTrLlB0WjOk^/o9gXF27@o]\omJ
9R+!5;e[lXSjC5b?:LMT;)<4N1*OXmr<("s%4"P<H?`K)LG&H:SGMJcb5uO!)%Cq;gB4uUL[3]peA$?-X,qbAea)>)!A2kq@]sW^&b[%;]>7YEe[jp@b
lt%'a/?i*i#d6B9hI*^O8(b0qFjjr&::"uHb*Qm'1;RkoERlt,a.OW"j+,.n7u:IYN3%Vd5dOSc&DYgI"l=X3`]u"'m'qN5F,tbef*qGKQJ(n5"([hne
MbPLfd!t^#>p":)d@B)<j,E![`<)EFQ5B.VN\p(`V(3[$&U9$b2[2f^DjMri!2S36DAEp0+HdgifnV.cuubH[\a1A=DQXIaLf:>@(g!`W,ef"[$^pP9X
*`ncs:f0Hc'QN(Pq$53tgCY:UA<jh1cLl4,@KmZU,p3oV6`&U%d8Y\7a:X0[%ub-Q+&U_a\.eSK1i%g3q@:+SN3'ASi?YH?VKB3]<%81KYD,1(1'gj[W
K,kL[]l+E6=o+aMIiT-3mq8dL"cG>d`pJC\I0;QI*1Y&=.pdfZH6+jm$1jU1la6=8r^ao]J68]K'=mUbcBRj20*GX#q[gS(S!U"/3PJVVBc:*gKSl!AS
WIX^]S,FaC(oFW[qkF!'@k%n9paS\FFR7%dZ%!EX1Q`d_NLKq#dZ;C/$+DBAbGq[rjiF^8<\p]:*:n*/K(Pi1@\A!Fg_r7*'T8_BNoY])2e9VVDT'pQ)
#uFJ&Rs5JMXn0@4^eOu(^%r=b4/dVYE2aI%*="IY:A&58i&'X[%beqD>dZOMM%qVKXU$";NmX9+?'0XPBZhd316l7::;gmA4k_s)d6PgLQ#K(aX3[N.A
PW@_$UtCJosNG[@Yc].$`1?LU&r0'G_9NnDs*M-G-tI&;cqdp6@b)%4g7s?PCF4*%deI-'e'6C2O[i`9IAb!A=Ijaj77-[_W(b+<Mp[:EON?-[_U?=`N
7HEhYbM'F9!8ATMicX-ks;tGsT#Zgo1/$REsir<Q$C.7-]ep=Vfa^Y7GEp<SOf@LM4NEeg>3aCkEMf05-8[)deTCOM"f.pm8W2:$+P?IG;]6ic.RA1P:
Di3?;X)3E+fIs'3_49_,"G_LF8nq47$l$unppahWo?&oA'^+tK$u\=>;ta8\FFO1+=)q6(P(<NRbq/GNBaMe&k<I91/hA,kMl?(hI\g>pM_diZ,Co\+(
=`#<G>J/1SPh(dXn$X>>@rYF)Df.K4&3j#WWL9CK^i#J,V9A.h.9@EHIU_E]Gc)PJtO?]EU$VLG'Fo=(pg"!MX-&;;p.@tG%cbA]=<c:fj,2Tm+^^@,K
`=Io2>%uplG&1'PY/ob]XC7/Dm=X3.-X99g!UL])pXr/m@^5aAWY+QdHeW;]$B%3I;FK/o<hdX3>nr-!nJW)0Gh^#rghK3[7+"Z/];5kIC26\ID9'>DV
6Xc:E]Xm0MoMm"\EiYpChsIum7^FLRPn1_2-[:lBcEhgDHdV\[&U8e>S:RY9V2Ku3^V@\@821Mi(Ma6)K'UIPY5CmG7L^p/hGFeKaLG?ZcIX>h0u4)h.
lFKpE%eD.B+PInh]iD*Au1RchM=iRX<B=r3qF@.I?*O+Y^M!Cb`Ko:4NhIlaSk20>:HpY55-HQbCa6;f2%AdFr]c^8V2D-/'uf,'):7R*Mqe<s_f>8+W
kfPYW@nD#(W)P,oG6ZQ=e#-5T>AgWQJ+`&jb#2`Fqm&uZa.e29n^d+(`IWcp]8kW)6dkKtXBUBWqpmDOrU:%VpBZn;AGhE/^Sa&f?/V'W?5fN,k5WIV,
\DA91arRJg#ULX<5gX%@<SCmGf],WbSZ@P*e)X@+p(gr*5/&]$0#Cl\[mX6Et$CKk`.+\O6=oQOgp0Vn5L%?Q?\LG]\!Ra4-3q=RB0=traJ/l:o["`jh
l]YRnm#>gWh6=/f8#@q4gWkVSonW'(.TprAW<Wr>QMIHPDJGIM)u7cepW@@/8U:lc$lX^;Mig(QXG3CfopEaGLAVql$?%0&MP[jXF=,8?fJ-7k>)^<e6
.5Oc6+j[_Lb!\!Hq;7J78sjVR>E@f%:L)Lb'0@H['o@aSncb_##Ek;*/h%97r@^_EktO._!^VJdEMN)<Mm!`':Q)F.j:jH^!Wr;q6&)89PcMD'Z_tj,'
F=MJIT9q7ARe;'oN\6bqfdBf]C2SBr2FXd$4Zn;nD)W[:uWkV.gdX.=^fk7h>%AU3E5eRs+;'BP*7rWlh6q^u#dC>;/D=;**cA-8@Nk;@]r`8S$Vp@6=
4,40@=^93h#IXNMVG_;O0UAXd,tMJIW4_CjMFN=[@A$<r4X7Yl6IUNrAR20mdr;k97KL[pejDBGu%B/X)IWX$Q/9A-P;UkhT0GBPUQ*N9dC1+SeZ.$Ir
e-ntVAGW"#CiZoKDXMuTb<nh&K4=PR3)R!%ibM:ce]ucD-PLGF]"5]%8phY(W]=)=m0Xj]4m_ooJ>K>j$IOF:QheHfcB'3H`VSmt/Q7j;F(ZI``o%18:
lC_RqS-"ZYO:/F#K5HKa61rd,_?%]ujt#-T!hFd!(rM[kbIkXGTh8';fT8*\U)1g-rq<_%ITU_NI!5GYjRqIfeGNZKd:45`OoNcLTS7.]&YoJmpuDZ)g
qUC"ThNuA]mIqDg\:F@V8)3&*oNGu3#W@>R1&1))Gg@":AS#W,Tb+7)k$`WO7Fto-Z*"554q/In"=O\8F6@L?[mS.nK+0WSPkGGi#IB^SK-9J7+':);>
h!rOUC1YDaDr6,s+)$mB^?Lh]o23G/"*k"e'-ScJ&T!H@IfN8YCb)!3$7%+#E9YWhlG1&iB5E2X#gt<l\<sHKuO%?"O89ZJeoLgQU"SR8W4K1YJHc.Bi
EX_YE@`Eh#ZrpSho8)RI\Vi-`:>+?nVdGTbY$c3GoLACG2FO$bH^eUk3BJ#\3f^]a"o7AC3rM)Yof6fpT8K*b'i3XCT.O:='b7Vr<8"k7:`&_iu7/(+(
+bk\07gqH8_Ce:Dn(1ea3B^-)s#NC,o30$Tm?';Y+,7QVQZ^tNh@taI3(pO_Q5H'I*qU`Nr<mp\*"357.OhUu[A9>\<>.2_M,T@=/+HolF--`0#bgmLG
*`!1r_!^m3+4^:cH#'Pg]<mBiI6=fV4r`167@`%*aqCu+@Mup/^VGm))(d?i^N$#ab&<rQ3ALKsUhRKIbc\*IQ0N`6%H>BnPs7$%_\VcVHUZr\b(*'7l
mq+'[UL`,$_Zq&)aW/Q4db?aghnmMCJh#9,Ho[[g,>mg;-IcfLW750fWm`AcGm(h?XN/g0.M0t),o!01@Sl_SMAa.)&O3,\)f+=S$F>V"YBSrW'e=?oD
6rP<G=uI<%En,gpp)).Rf9Si1_XO-M_Z=ag7pFbS:$Q/e,.PS1-$*o5"(X>DfE&kXl58Ob?Kb^(ahiDjXHOV@tY_-ruN9VtSEQ+.tjP4A0Z><Y-U9[!@
V=>RqK4gEXo.)f#?&l[(Qilum=.1hal#]rNbuhSEPYYLM8sDHnYYMegDnDBoNiioJ%ZAZ5Sc.5C48Z[UM=YPOtKOj6mB67^C@(+dOY1"]O&c8WUn$d,I
5U^T%$4Z3kET4B'02&*N9B\..N?<ZpVZ;r`+@S7G\VdZbfQ53Y^Zc'PE[q/GRPWQ5Zp8$5\'NRC\j0u'%;3HD6Z*(k)9;fBU`,Ld$pQhE6"[!"KAT:`.
4WGCL<YBhBlIP#U-67ZZhm,L7H]u%g>jC=&g(>52>LBX]_9Y8d:(MehD2_>'fHBZ$k\@cG/*9LuhUBPIpW+1;N\Q2F/Wu-]?\F]cleE+.IC[!'Xbiu1=
XG?Y);'X76Q`;C-E`,moV\nB75&/p>B\eaR"V)SWsNiOnpkkW3b#;sS!AuPL0/"ri&/@RF&cB%^b2f[-8[51C+1BqQE)KJXlkhB?j\jY_P?2`CQpBl8p
AT^9+u%s\Y65t!c'[7h,]fCnT7fo3,clKKjbL1dI@*hBDGT?&SakRg-")Ak*8B$n$_+^(B[,df57Y%oB8g';fgJB";C$a\^epMeYLMSB;asCd_51Sh:4
7I1(h9r/0MGk<R6pV'f/'n->$9r.$jYm$3nK(S+b:k[nS^Xhe-#uFY.h(YWBJ*7^MsMi7e$UO6"p$&GbRIYU`]++NOBjU<?hUr1?]YHo4ikSp+o)=92B
niEncEiXr.;iGh)jVo3D0."nXoFk5k+IH%M4S^3H_WQH&@G6Q;3:uK*A'/=OK<nW5F!K/b<%;uV$aLY4(=JWP<)\P7)XZ[_H0b0H':^]^d,qlWZ6..I(
b=Qk;?=">HbSD8:AdtOk/?(+.=r"*%qYo-7eZ>'-N:uW8gSj&Pa\@`&3u-FSFos!u.m$C>73Po?0=(k?YdA5sGeY&3PQ*14->c,e[tSMPC4oSDDQV%",
KnB23C\Ni;K]g@XBKAj@cGM74j1HPf8.m5d;G:eG>I2c_4;Bc"'ab?A#p#DQtqsOZRX9Z51sNhq4K@>gjo\h8k+5:GE9b8-DjW&74nC_4jJ_HS=#8;`V
cMRhtn,.eC\_p$f0U>.^[tOoQe1rODW7Oo`0)@R8T,sAiT3.p(RY+2S#X5cGD0[8]I$*eU?S(X5\Q9Gb$@76:n4CmM8!Tj,#dGJX5=1YnlY`B9BU^&ne
!B7REu&?B%[*GG\meI@OuK)*YSD0^0J%aeMt!kLQNmBIgH?EM#qb.UP25Pp;1=<_K8'pk?9.9db-t;7Ej&diqVY=RfgaF/gC-1tO2<b"YM2'On5R4P@n
OdC`E1YXZ1LOk">tO9KZcTImbr39"D"_Lf/BfUV+S"f5ATM*c8.e6P`2FreVK@'?,p?-;O?@2RZf21/hPS#mX)$#KA0h+@J'iJZ<E:SIC,qfPiWV[Li:
H1W2;qL!,g!B--5Q;,cF)'J0c@/KE."C_+->TV5-g)^Q'HuZRPW1cVnJHUo&cE8H7]QY!8rI]%B-XLID;e!N2;;Yi/(W@,.cGd1B0YBd7FAQbVhs4e&"
0T3a.E*Sc3IKT]Jjs2g6^-X=D72OP!$L^"j-cp_KFdV)O7-C29`6XA";;H]jEV3Is):!/S9dH+hTt$^+SJ$m\UtA'M,T3RjtX%dNu+6Q`e7Wl_8W$3A1
XlU0D(NF+n.mk!2BgaYh8l4\Q6,hT$5P<VmPj_$p1`=gQeZ[1Y0b[&)9*F!J$,h?.WuYEKBL*mCoZTHfaBFkl2:8)+K%5q+4,MjarM\o3A#B;X0Nm[US
8B/0lksh#?FkR]S:B;J_,pK\,15;_Pq(JJ0Rf=gQ7BL_bOpe*TXh:Uf+p;;"?-M;pS&'_TH9O5a'lOrQ_u',DL5r[b=["!%:/.[ET&<$XgE3)pb&cd%B
o>gmOQ<7u:G9_ioBB:9?h%H<*^S#ijInc@50OT-Qe^nXsJ8*N#3e!oB!0E,E@aA4b<K0U.`5:P]ODjtl`?SO!F+p^(02mA6Dd=1ZQ3ordWTuq*3\&@'d
HY.+XgEioR@!aRi5SU'eWD'KKX4(-kbYtV6fdQkZmM.lhC9rFZm:ghEr<l5@6W&.;9)Gs=dG@^Bd`9k7:jUkgh]0@YpZC#4j6)3^Ml5GQ^,S]%q?LBIg
4'=O]jm<n9l.K4jk$bU9[%Fogm5/5bhCPA(b/dd>I![7n;e1!*RVCnG1HhdS':SD/G!XQ9PsMRXZl/%H'L]-.(ms"19c""821I1P\J3nCX2Wa+1^Xg<o
8Y.<T2p#1c9esRFP-KD,<1aU-hje7*R6_6m+7#3-+8iJSek=/L#HHRiCoN.q6!oUT@L`BnZ]7T&WJc/bHrmjjO56VJOaXcoj/%^c\4c+)i,E8W&&KM.^
3)Z/O(0SZeRoi7AoXK^Z7rPs81/!(Ju#9jk01F4#b<Il*O1pd0aM;*>Am/#=a5;K<i$fb!Om8(gB(Ol*to?.HINX9K?>5/c90fkn8Y@b3A-J-SfNY>r4
,/s,:.7cMI:lPdk7`aJMkP$b<B*W4$eTSOmmh)HMOa.AH9G;kR=Vd%l]%!DX%2UtfiE5to0AXAmoA-d%O1kH#\DQ;chaVS6s2e/mlZ6?,b_C.^tL-^fX
95g\/8n/<q,LmWLQJ*5h"#3+k>FVU>.*/(R5#H_hA!ZC@*Ni<ImXt!+d#&mJ%B9O8gLsQ,0k2JqA?3\KL/,c`Tq$'_Ju&(E@XOr?ON!n+X:Q#OT/0Vm-
uehlW*''TOHGTUW)$M8)4)P/Q,u-G-\G^Nb18q:V<X&XCR@26%8JEaf1O.e.eQ9N*2hKjIVoZ2'NNm#G#\RJ:+PO./j@n.$Ho\SM(tndEPLsN:5)'U1j
a&YNK=Vj.r"hcs%n/=Q(k-4[S*,gF&=AVKkt*0c^qc&ZB>n\b$1*4M'=T42Cb`-f]H"sq?0ZlcO*](X.m4,(:?d\("R1oP[2\mYiq5ZYdE\o6aWPBs!Y
#]H4ph;8V%Sqe=rjbo-UBiht\#sbJXZg7(D3!PLu<o^MV/lH<)q9dWYfBiV9BM:6\?TeJ=17bd+YZ5YP[GWN9[Ee[3-=GVn(@J7`+6<GC@*_?!b"qcr-
'X#CaN6K26`\QkqK3j^68:RpU!Rh\i1TI'3,gOUr.J#2WSNGBGm2*+YSH,3EL.1\8>]EiLR*"8`#.TYA?Gn!7g4-n>nI+Mf%nSGNH>k23fJ?Q/==]&K_
@U%ZdiaTame]F.p#q/WNgqZmp\5;fq&Q;42&qk*5)<ga6<Lhsdg]iQZd_P7AF](E-gr!eL0ln*rO=1B7N&-^Kcr&F?]8#E0ZVk9ad"M\$5F_OI[`mpRG
u@R#71:K2P7e384nL\nX66@D+1(e6HW:b3[Lik*Q'NmQPe^?`qgat)(j:L!^%*E?p;?feE.5i$TDlPH_-1+/&uDo2#Xj1[a$pU?M<pQ,=_Lk^/P\3q+H
HWe`=+?j[m8JHi\'&\DgjO70ZqO\Z-(-99`[S:j_Mc51sE5BQE2=,n:L^O%FJBA?;no@\>YO1Eqo"reajG?b%tCCd6j@sD^@Pt##D:ckDuR\\0>Dg6OQ
e>*`ThHfGSos0*-n;o-fb4]X53O24"H>FdHN&l+A<5@JCbd^;(&Oo#o:S#Nqa9<q'0<'VHt,[0h-ak]V23GZhUnP*Dl!c&]>0^u&gMS7cP+UO:mT%Tou
[O\ZG8(]4Jj9fX[)?c&eY@p6EQ,R`m@oWl(i-O41ZB!qH=mgo?8D2I[dB%k9>Db[YaO2U?)IGo;#4eW@tfUQ;n,0kM*#n3+t4@J$Knt+285l[@;m+$9<
2l#o+H\\Jk=&30E-@^F>in^:/MIf`j:^MBe;Fi<;OS/;aTU)+raL_mNmqTT>A-CSQPP0_5DIGXtM1:dr(*CnC?osfh"=Zr3(9$+4^"<Z;WVMMVL0fX;4
<bgC1)#3gn2`t%FBTW.BCkZQ4eF#+M8,f$!!7CM!AV:68Sc$\Tjn-;?@3Ba[0]lS.kO$r/>/5_5b%tEX3FcZs7INIW3QU?$foLUH@mCGH?R1YN1k8?+&
eh*2_8uqmfP?pf0BK(d3[R>!S!0jLC5Xi7`sjZP..2Z&XmI3SRR=(:9W56EP^;FlT@2Oj4'@fLh\UrMI-K53]/?G`T<$pGVaU!f/!!Ejt=9sZgND2@Y@
r?c-aH>IlHr$/i"q_QGnr0p.Y`KpZS%Z?ogFqO_IsG+A$CTH]j=;?@rPJW/71>gEFJY>\:c]Dcp\V@<>H](p>K019P1p0Z&qq'#p50Wf"3,[F!e3*R<5
2!6O`D)+%GM.&h34+Z1R](fQ!b%+M<KR<X.c4QG?Abqo,biZ4DL$pZM>kSNe7RI,E_@AV8ed^tWc\)+lG2p[Lk^'$1\q9ug.\&].H!rCN`(X),EG>j*`
8eRZd9Rj;81,(%Sm[7&qjRd.CQF`KAh.)OtW*.bC3-F_7>L=fh\#%CFTja?]pB5Q-NQ\_X,HBE@pOrB68ka(BQLX`a^"6Z=[q`B.@$K;[B+."(gm<U:U
5Z"o4t5c^[S`0krZ2@#q)RnalF>,:ebQRIG?rnZ@'Pq9"?8+N&G,4X,&-h/Dn0(\,o=AM?71(jS$NFBDtSKfI]K.>)U]e;-8BgDS]8HI6/E\+V36ZST=
E8^ENo?::g\Md]h)KOeW@_NP.k^P3Mht+'m\9[\UG'^%:pj'R],neVmTFtgU]1O%A@r#g6J=tlFSBhoL`rh`)Urh%4kLm1-MKFFo12\qUB\pc:co>f(Q
Ka1Kf#M`iZhg7?KX._/rH(=Be=nAO?H[AV8KCIB(^Llo^bA;)kWQ#\EL+[Gn+;-dP_,\kNg-ZXUS9*[t<G$L+'5Nf4^)TpP`p4i;K.WMY(/<D3D2!`j!
+f^ia]q_pnSgN(JJf1oGd$&us5_%;1)!d$7nBl8WT;H1Z!:YN1k@(8O(^tCB-YT:DHreJo,*[._FbmH8LE+TcpBWin?Wk%)+\=m,FGQZ"dMs_k6kGja8
[N*9C*X?!A6RN,oAbfc?>3f=r1=jGB8b>/2<5]soIG&&`9'H.\oeH$*1jh3=$O8KLjb#I>e8R!c[d!pHrL5;P'Cd0qG630(=BLT:ZW[uWCMYJs*EOFTm
!<!Mfea[t1&AT[E:iM]X5d:?@(fTiJ(sD2mnW)*kOE8\1LQl[%90`3mS8dtf0-Dp&'>:`=S@+JbTuMC+m$0[D'g'0)[lZD=[IPW%"Z'm'%,sd+sSO8V&
bHWS*3U/JX#Ki`MiE&XJ\!"F.Qp>o6"8<QOY#q@BoJH.J1Dflr:Fjrp7L^KZAE/:oU#YFcK*1Jd5OU?2bKGB@B^7V#TCucmcghJMgR^)uAJs?(_tE]ph
`k07/1nK`%/b9a11Mq/8n1.1'\o^BpDd$oTC4=R`.A/%3oE;c.";fMqVKqm"rOE-Kml8D#7,bL-7rd9S19--d$D)YJ*WMP&=^JL(&+=N-MW#%KFZ[5]-
b2X=N/)aA'eMc<ZEP)-=K*:Y&n0h&T&.keL&(?K/=V">,:9C8o2gPY>hLWA;aWAJ+_Z0%#,idQUcmC]X4K_.U;8@Z+l-s*5*4W(A#no4p^l7.%!n_!mA
rj-OrL'd2!Duq/RH?;G,cR9U%&X:oX0MgjNaLgU=lpC1JNNQT^MWuMQD4]""7-]:!0E7+53.ZMls1eNas4=`g5./:SQ0qJO:<-p0?5Vn2ks%J/htqePd
V#3D/N<EC@\WdK&mIT3+?O$24kjYJ)HQ0C]TH/KDd#*LN0mU':^<J=pRj`A'7&*j&m>_omS259SA6:\ELiUoaGXNR3H=N?oRcPRkd;I$B]$%&0kD/+m0
OG!K_69<o!]o(?NPb!Kjj[@;aHCtE>8l(LAq):g)k<(kcLt/Thrl*TZV]dPAkIm.V9%>dZ74/P'KHBB/d;?B4^I$;T0$P+]CYN)>fFd8`2E8''gsnp!M
:;$sZM58LV/l#-?8^m?fs$f[.`Z<EqBo!PGl[&i>l:LWJ]f8ri0o.^9CA="!Yk_n2"\pm&Qt/i%O+Y/Re*U)T31$oGX.q_<3*fNdDS@m;ZH1)M[e*4BJ
?0M;s0!^AY-rRa=r4WP#ZSSq$q6a-(mrr(HoIi>#X`,N*%ibj-jp&TmOlTZ]i0:=sF)ab9q157RroEB:*)2@^g:P+hM&_Uq;3kURo16uNc!UI$j\h0R*
nPU@dQa")flrRd3/[g)Rh[ep^a+[D;.tm:nfAbiP1h*(HA[`63d5'#pR;3h_6_]tu6bSBKcO]BH?sM$<"89M1:*4a3^Im;/W>unNBjX#spG!o-diTE.D
^Q)5Ksh$pi_&7U#mCOfs."Ea';1J9722i4YUEMQ$A-B"*YDsFj+`0'=Oi]/!?^H\NEiKZ1(DL#R!sh;j=%/n-QhIR>FDXPPd^fO)<!0Y[RoZr!,a-'[9
h,oI?Es8"l=?\nu$q/&m-rIld?^6<pHHH`IftKEjWG$T^@P$o9D.S[0qqq/N#-7ecYoF]<DmnbCYP.9=`F-6G&+-Y)&@l%rkr3Kd*GfcsR#Y(St=lR&-
LeYG=<iD:UCL0IS>G'\3uP_JhT\5Y$h+a0T8a,DH8DbRKfhKhfO.OE"`<DA+6>CImP&;E]"M1'eQ-"KN\4E%U,qm#rUq@[imGdMb.\i2si*Yc;uF/[lT
N3rTaK.9fMf6-5+XQ5Nj1XG^*<HTulVi1a?8Ig<E73RZ0M::oNsFRjONrMFu-4ip8g@\$t$L.It+Uc62'OZf2UDThd&ncQ<aFS`js="%R^'V/&)Fr?)-
:`WQc1`i45<eoZT<pT9k=Z_V&E![ck6NHi@)kb&]5A4pVB?;?,*)AO$.7>j?*e77qQUi>^"\VV.@JDg%-d%+PZ#N8HQIXRb&4[/<68h&H,FZ%r8H1UN4
;CYiq/"&E9fLJ)fb^0uB'cQNch>D+YWd(T9S%>fAf0?c=3Dt"U#R>j-.2nt:'m(C"/4[]Am?MAMb`EpbHpHcq\XN@%f7Ik/[YU34MrYR!&Y#."MV/E&'
<p\G"j]4YX$^f:cNDr=!uDg)Y%6a(QPcS/FZo%N0gdp+`<9qPue)Xq@45"&.60@F(%28Tk]PDFB:ptd*N>iX>WM!TmRM-<60C(gk"H/?%9pNQ5.1El]R
';%AInD9=rsOF^&l!W"8j`)^]M4B=Ft6*V;8f/,Er5P^gkVaYNXkbha7D!)g<Hpjq]a[G)s"%dN<C5N/E@"X)5tW<:J0XOn9p*b%lrDr^9b\*tX?2@R;
o:/B%P^Q%D5%0K:3FSdkAf`.;b+'bP>@OA7\E$Cb4M^][SV:EZP0k=9MMIg5A8#(W5?AKj/l^QULAJ=;Pj@cd=-/2/XAX>'mqc:=R\5cG?PRTW%Ti<ad
#7uk-QWSH_g/iP:_T.d=>k2tdot'Jkg<NrIa*I8QO/n4fD$:1d.]jr,D-ZFH*#+Ud)60BA]t\=:r+t>,kkTrIgE0<N"F]@rDp*l5:(]V4bOBW9D2i72b
X.RO&8Z/0!X>)!QZc]Hh"`1,Dq$g*?'&)T3T$@iZYR[!c>dkniDrm$=c0]i%gn.o6*54"9/.<nXhE1-@c5#trhjCXV!;-.g0Xch.c6Lbjo2c[jLHB.'L
Om5FXXh.q%0t[JNKqN3nt8GrTWP]XK'R%,5/A:#scKiFeN5%;RcfT7r:)!clL;un"`/=P6T\ScilpXBMp@%nWH-CM+#I=>lq&A)uLK-)kbkpYpRf?c"%
iol_#O-1eHn82_QNDH-fJ3]5NajTDe8WUK8gmQ"jSU*r%t:J,H7cs2C*>!OkaujCVhej_hqDHn]<H6rJ/AGeJYtJD=ubWmHVT[>aGR>&?&<)9f])Wj2,
J@>:"=TQhsSdrf5S6_JHcP30smWU0uTa-3*8E`;)p+G[b=4Mp-W!UDs3IdujfWtR_oVFPjZ1.#mHi6,H**T]gtO*IT^o&Al`+Z+3.A\Er(H=hljQ(C>^
JPA=YJb6RPDpn)\*'a>b,k:p1O8nU>s7kLOq2bR9TE"[Ns7q`Uo$;g`?iU&EJ,SOprboQ:5!=17FG,?f;S/:UpXpH[G\(:5O8NnN8_X'6s3=\I"5/'.;
LTNG3$^U9>o8!iWPdq:b>sF)NgG<nMMnEdl=@4Re$5^ba\=N=GQauuJO?.bHB]Q8(a8MTe$.rq1dB$-1NJY@[nn=C6g\_;%<K9@&%k%sCp&\*DK.Vb8m
qpSasgF'Wmd$mIs?2sD2Ccq>?%Zeg9qVlJ00J+kO);KB!SV-<aA,#8NZe,!L\*X\I&%$0:qfpK:IQiqARBGVh9Qp:$+-GQ9V$G5W-GO!L,PU1QlO3MWV
q7"CJOa(Pbd^h@`EQH`\!G#JN3IEC*6t]/U3sHF'82W;5Eq%,9>h-HGC9!i?Y,hti'E_uq=s9+W\6kF*Oh920T,\#fo(1N_<fM76^Q*6;A`Zmd;iqqfZ
="9U0_nI>,D^BGF2OJ#3<iLO!KEK*`GTiO@dqtc$n8Z_Y'a%"=95a\lqOs&phLi*Gg+V-+:=5c%$'FYVtbm]`UJ!uJ??YX3kHJ<b]CP7]t>`RT>$*/65
J5pAV&Sf3%<_-qb"^pTe_T6Ik+\:W\g(o'@'e;7:d48N'ap/>WJek^V\bHmB@@^h3i=5'`JuSou`[":<6jE!%-JUQRos:Pf"Fmn;1b'bKR=OmFJYFuum
6"`eAXT-Ll);Mo^O2DK`_Uj(5i!cgMk`uOG7er/@IfNKr7!%,9n'$ec%T&knXIJ/PGUG?Q9LZ`FIN\oK@uioTo3j]cWfjmgV)D^ck2#p^V7(.U9LW$7L
s?`/Hf`ocJ-qkdX^o@>@soB`r)=nrI!Y_o\sb<G3b&V;pb"+p'iVrOon?B_[46Mp2b-_7$ut3&,2`,psahfk2$5Pr/eFY-$%TCHUh:_gNMC2X_e8&I"I
n6nZ";dEU9d0CWL<>%6P2[FR2W<6lK0jc<G"DL3q;.L1Q%4)E7nCjjo2f@>O(^%Ct@X0"*f!5!!%!gU2+Rr0Rl])8uSJV.gY8pufAZgkS"q"20_6,DF5
p1<X(6@KU,%O&W*SedaRdEB</R6Ad$RI5eON3aoL9e-h$6=O-Q+\0$L'9th<^H@-oU`Fnk$+L^X[nCrA6#hi2%Bsb!-C&=m5RW(bHpX]`iM4OjDaYrY8
BB/eu"+13Y<o'qAlR?WDT-XA*biV%FJh_)BXhno`i+^BqWtIHl+t6_e/28;]PTc%n`PU<FWtma"r)E-%nV@]Vpe.._<N2qJlkX*&J^^-Z.c0[roT7efd
fnLIanHT?nU@fdNZA<DMb:$HKtDZH((qOD`Qbgc*]cViD7I=Td[1-@knA97FGbonL(n&iCh(gFoi!e!ZT5E,OdM(\LpaR`jMG-^5jADH2nOsY>3F/Rp?
T^mQXil\A_Lmg:HrRB?-pCC0+H1*pVoQ[1*;5?=W`W90\[0DVD-[9I`hXB^o3ee]\To@$3rC0<'b&>h96O]/R!1cjPHtJqFk<0e\m%VoGPCRj6@IL,Pf
,-/5<):/]7E3rI`?`55tucaEB]E!Yg>H@bM5CBa`R0Mp;6?U+,qL^N]/n^LMVmFTIG&Sa+d>@AtG!__3bC9)S+n9Vl@_$6DWSf?.B6hTFqYr<,"%9d75
`eMHq\9fsQ[-7YSU?B$#IG\,T`J%G,n5Q!E-h/3dO)\:h5T!+L6hlhNUq8:t=LO]9GBUBm$^(%gtSp^in@/3+;3gdinZcLb_I!c.)QJD7agl)+)Ib^"^
90YUrr,Y+%,4a?7r+4qBrV.mNI=D)Bo)J-u?Ut+'++J@4bZ,6+2XXsCg*hrbEEh[3#2CBejOQq!V@P(f^+f`+mtLl(JF:R%WAsp:3VT9Y;Ga?f@f=3$=
p(HZch66&H&4BqSn'6LRB`2Ds,jgfi--?R/s-'qo!ll$f^m)*G_j%or5d'mkM=5Nqq\Hg+7elJ,UIiRhkuAS$;;Un/QuH^]p?*lYsoN_&Y7%[rdMV[29
#KrhqR&gK$X:4G(k3=@S4MQfR>fI0Fms^Z50O8>XK7\W`lo.mI'FI`5CV\p^m=scpOgLWsOQheX/=E<nF5GW"p^M5WA#Wr3R(fGYZ0A7R1Odcpl5pJta
u4Kk3YE[)Td</U:UQ%Bo#8Z&KR`2,<*Q'IGY>IcifYK;OCZmA[['6WS/nXTK-OXY1KtZ>Eo5FJ(=02-;-;!Bk4ad>MF'n&PE'\K;j1r_*%X7I:$SJ%gm
?\+&R]fRF?[*l\+%r:rDIrsF7iM>b3MriOR4+`'peC799AFMhU4"Yqmmk9601/D?+.$:@b-fD*?^_(D0>6/9,dZ'uU`7^m^k2N\4LJ(+SQKOHI$>m'6Z
no/l]4BNXT&!]Z]Del"hJENfkBW*G_XM]"h]>k#e8FYP.(LLmF,^u1['#N.ZF^u$n///$_)-n##'''
	exec(zlib.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

version = '1.64'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-11-20'

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

def nothing_to_check(header, invert_match, filter_patterns):
	"""Why --check can judge nothing in a run whose table has this header: no checked column (-x leaves out both,
	which is also the only way to have no valid output field), or -v with no pattern, which keeps no row. Each reason
	makes a healthy-looking run "could not tell" (3): a check of nothing is not a healthy one.

	>>> nothing_to_check(['NAME', 'SMART'], False, []), nothing_to_check(['NAME', 'FSUSE%'], True, ['sda'])
	([], [])
	>>> nothing_to_check(['NAME', 'MOUNTPOINT'], True, [])
	['-x leaves out both FSUSE% and SMART; leave one in', '-v with no pattern keeps no row; give -v the pattern to leave out']
	"""
	reasons = []
	if not set(CHECK_FIELDS).intersection(header):
		reasons.append("-x leaves out both FSUSE% and SMART; leave one in")
	if invert_match and not filter_patterns:
		reasons.append("-v with no pattern keeps no row; give -v the pattern to leave out")
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
		epilog="READ/WRITE: the first query shows each device's since-boot average (bytes / time spent on I/O, idle time left out), i.e. its typical work pattern, not a real-time rate; later watch refreshes show live rates.")
	parser.add_argument('-j','--json', help="Produce JSON output (list of rows, header first)", action="store_true")
	parser.add_argument('-J','--json_objects', help="Produce JSON output as a list of objects with numeric SIZE/READ/WRITE (bytes) and FSUSE%% (percent)", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (read/write activity since boot on the first query, during the last interval on later watch refreshes); rows with no throughput to read (macOS, -P) and mounts that fail (FSUSE%% ERROR or TIMEOUT) stay", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2; 0: no limit)", default=2, type=float)
	parser.add_argument('-w','--watch', metavar='SECONDS', type=float, default=None,
						help="Repeat output every SECONDS (watch mode). Equivalent to a trailing integer positional.")
	parser.add_argument('--check', help="Health check: print the rows that need attention, and exit 1 if one has a problem (SMART failing, FSUSE%% >= --max_use, hung mount), else 3 if one could not be checked (SMART unreadable, FSUSE%% ERROR), if nothing could be (-x leaves out FSUSE%% and SMART, or -v has no pattern: said on stderr), or if a command that can hide what is checked did not answer in full (named on stderr); when all is healthy, print nothing (-j: the header row, -J: []) and exit 0", action="store_true")
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
				read = results[0] if results else ()
				results, check_status = check_rows(results, args.max_use)
				nothing = nothing_to_check(read, args.invert_match, args.filter_patterns)
				if check_status == CHECK_OK:
					# A run that could judge nothing, or a command that can hide what --check reads, makes the run unknown;
					# any other command stays quiet on exit 0.
					if nothing or any(cut_hides(command).intersection(read) for command in unanswered):
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