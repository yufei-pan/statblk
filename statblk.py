#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shutil
import stat
import sys
import time
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	assert float(multiCMD.version) >= 1.47
except (ImportError, AssertionError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE$ig8-O-i5'i*R6=FBnkYLdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh*#BVY2@n9=XkOcI@DKhS;F=XYf@.
bkU"!;JY/2uZq5d6W*qmS$*M-\,Pd5gM:^G;SrceSRe-B2<VH6Ya:5DN5q#E@aeCT\u:L=Ahc3b=*V%>Cctj(2ncD(q47UQ/T['Tu4`n!B,&"9c;Dp?X
$Mt3`>UhCLNd2)!\2+QeY[<Ld@R^mOoJ9%I_T>5@D.V'T`X>3j7@/UqE90=Li(ZK@\[6PX_i!c%e(RYrSgB-#(M%JD!R`+"%C.LPs4f6,NOi[csmhntR
-llggcNB6JO`h#?qZ+3g)3@PanuB_`LSZf3g\r4ETI3taQ\$1Ip\?+6MIf8q"3KC5_L=fF[F^DA2H;Nq0Z^0f-*o;;IDIus:3#%ku1GW$!@?oF"1^\,$
r+@;;eq>,?5Bkj<\ZW8g/bT=1TIGTc+V"f<;/]*IQbUA:\*1aM!+dN@VE3/j',.P9fWaeWVn6N(pB"uW50>`_a2sT$A&-qe[rC-j=$%Bo&psb,[EUBLB
"#L:oQiq"!ho19f]h:Ir3:`gSZHXH7Y"^+n231\615&fFFL<l"-VWt<1;ammd-XZLfk<l6hB,mO[6b;cWQ.bPD<#OS6q'@1?eOlh0)HH*]2AN]bqVFCQ
usE7CA#Y^M(<I]X:6[MIDAjI5(TSY`rN*mNY4OKL!^X%.&)0ccTsOUk,C*FW+Fk/TCIMSs'i6DH2:?<@&Wm?p#=.BG8G'"M:=`0Lu!!b+lki\TOFt2T%
DEdZ/(>WOLt$FDWS'UUedNe#<aQNWMOfZO&h\sZQ?DdmY=.BG3U[MXg_2KcY,kQLJI*Gl*8N3nk\?HI@J8RTY"qE=fcpG2m!'q7Y-8t<EN[iBohQ(Hd.
;&3`T`Q\IcI9ACM%;Uoj^o@K_2:+&>!AWadU&N["c'-WC.CD3Cn#G;Ot=Z+g0+\,`H=?$M-n:Tbc\Gr&U4pf13\;c*r>6@I\:/$4D9mfoiFb=YKF^a]@
1EFY_[KhKKd-\?r'7\<,8PZ@A=#o5L1gdVtQ=CRZ_dM/Z#j'PJbHs,.n+cS#=Np7b%EoY^nCFWlQB"J<ld:l34]`ed$-Zm:)NSY$B2ifEjSU=MZ;&V%5
`W$Cu<GY!UmQ7!uG'k4>"#4-,&)25T/PEJ*_S,0)*4d2*p8Q.[OeLs*@r/)pL4EP#IXhCrrO.MUoIE!9_qEi@Z*/!_=/bdKXg#GYdU>VUB,QX_c(9CWo
iusRYl+dm]Enn!f-Bf.E3@5=<G@"^IY*u]EfG=!E%-lQaqYDnT&?3iC%SgYmXoOK:7%dSl[j,V&?^,[r?!DUoN2j9]C@G'A^6Em2B!8>SE(uXg$)E5:i
#4/KXSDq=8_4^Ymk3rSg;nG<(5])2k90.:4FRh?]nQ4I)0FUH+C.NIK5b3^D,l_r<e_!']",DT$T=[^aE;dM+ihF.-:!jf@8`cXLiV_!#6@3rlQ\hf8I
sTc&=1*BSIIB.jRF>K;YO#4r-oPYq2t]9nVe_6$JGGoSii$[%otAkd%W!]R"0.&J['!;EmF`EKBL'"K83-Aue]KW>CoNQ*FA1&nnE)ISY32n9u"E7Tk^
I.cDHoQ8>nL_`>E16jAotl6sdA%e((c"->b=lgT!(k4Vq;Ds7redC[tr$^RP!W[An<V.k*1<RG4VW3N1<[(B.bhU5:]b&AFjPDR<Yj=mEa3OC!1Nn_@\
)!e"gf@ljZ_fu,(`C2>W>"Gg\P%*fH8:0/2W=GrMf!Rs'hM/iKU4%^<O<dQ@?,%Rjp)cYJ6]WH7\@/LV86Zea&gI*:_m#q9bq8FSH/<T_4l&hrB__F4U
n;RATdu`;%ejZG#\qd<?*GNtilO.kJ;TFqrN31b(6eml`h\!ZM8qZ^@>^?@LTI-kN&gm:.jPHH)%kF?hbBM9ou.^i'Mc_3?@-F;=S8B*(c?uYaaddX[>
K$G9M,7eS;foJeoIa9P>8XqqS[j#?d!8dRnP)lO!rF(4G,sXRBr@8kM-lcep'"IHcG5E7Nd*M054%?pY=BJ1=`Rk2mT'k[C8BA,]o-pYe6L'/CEc"TDO
"'l+)0oHG*rYmG<83"UrXe(;HP7rITEkc"gSh(.e"0m,%peMO%!p*fd2OrGYo<^n6F`]kiU:W_4G=i$:s0s7Q[cgf->X-jRQD/BnXm!!:KZeLm`uDbct
Yeiu[+9g71mg3qQY#c_;@\(<f[fqoBOKJM/=kJE-*D!PKVVt&fE"!4Y.B@'MmGQ7lEQD,G+o-,V-l)XL$(KFlF/pdWF"68oZ@HTec2:c@<?6?_^qH8*$
)^,aL`FYs<:eq>>7Q?I1JJ+Qu/ktpI`BU^5Y5b3p9+.5jb2ef1ngl;>_b"NR`gH:f(\dan_otEO>l3Y8@)#'bfM`9\\b;IR->j3-F]=!&.aT\jSF$6Vp
(;20f*T9eC\;8_']b7XX+(f.T/?^7pmsWLS)\`V0&lE'Y@0QL#Pcd*,kZ*$]4/ko"'piq>8n-`9!f7OS&DD$Vhi[*=a$>on0bK_nIlgl0Xgaq1F@)c=-
UP*D;T]74/BP&\o,k(RH&_,IVdIUSIun)[\gZRoFFpthI=Tke3H`uG%c+C`MOo&9KO`m%Ci8:Q?"tioWf5/7<@URNj.;8^@E8mm%M_GbgPcsZ5)q#=h8
Lkp?g/8jW;B;?%]+S1cSC4ge6kJgGf[pGZQ,t#:VQk=\G<NO>s8'+cK>3L]D?2.W\r&q6S<Io=X1c0)uEa"nM)=+@1dT4'qfamV\e7bJ.^?^fO`ZcMC*
[,D.o4_(gW3PF<fIY>9]p>RKY_Y]$<)X]!h\RJ-l<\HPEo9cRl=U7O-Xms2`NZ`@cj!?--E^efQg82eF:40_TFK7W8Z@D)eqP`/VMcSBY0J2L30;@96k
Qu8&cClKj3[8[VEZe3@T?UqsRWPX1MjQ?2MPt;;/BhUaVLLnHV^eXYk'.&83SWe/=;*82@W.3-=EmE8@36-'to`IMp-3-WXZO3Je>e7D2H(]A)m6$h])
&RaU?^3a04Us]eX8a;9U\ac*Bg3)m3LO1mq2>:\G+>BYES*$RGGOjKi^^4LL2NP`A2Zt2%[:Q>Oo>eFm)@'p#/9]]bSqB"7.X\)9ArC<s&`;&NCX%C(B
'Xp+O3iq$k>CN[^3`"R[5;M64)NpPCtht15H4!,I\r.#tnesTb^t2W2ml"#N+uKNHghY*WJUEmI2iu+3_74#]l?N&."u?_Nk!b-`TmK<&gU*MW`e)L,"
C<?$q,CYiLU3K!#O<$%*U<Oe<MQlTUZMhEV:cb.o'T*UD6$huoD1&s_2m!78L:k[Z#[oOLaG#d419j"%lXGs4]:ZGF';l8tgFNBRB:7\(fdSMAj((N]K
ui(Rh^4@7iTSad@FE4%NtD0[=^29uOnM14T@TKKq+*e+^_7N+6G@+0<LT2[`jC;/Ig+:hkYC'8)li+Cu&Ni$]/*Z6FIqY"__h,FRZLBkL%9u;ZJdTN*b
$3TVDAfX#)nC:gcAe:ojjoh)-Ch=)0#:13_VX4+ml<k-3/[o5T;2&M4e1?_;SsJbGrrMU`)kDo-3,Z(o]&/?ZnJ`GFT\0bJ5N8?tQNjE$83Tq=.3^QeR
o)A8$eTTSoe*<7jF->T,(q6u3!q+lETSj4JgGgQ-WEUnS1"Nj03/g50ODjs't<%'[G$P2As4l@@Z/,[b3bUoOH^=/3b\VhO2,@$Y)kKJQuY,?f!ka=@6
CCTq<I76S"+fkXDbgb_Qd&.K6W:p$:!Do!F\YQ87MI]Ds.5.oYD6D!;N,;*cRl7IUUAmeRJq<-!IH,@""^mgW94OY*le/!i?X,]sI,GAML?rE>qphfkO
YJ,Vuj/]SUZd0FZ888Jq-m_gP;p0W^!*M1ku,dsnTf&mSmK,l++s+K<%22Su[q_jG%Y<NWi:a&pk($PdJQ6e;s+oQ4N`@S0M+Hk_0C:XR\fW]KmA4C_@
kDn,[/?'bf1FXd(c,IJCdhBkj!J\FuR4`ZZ5h@f:A1^#aeC0@?bos]m=5S9IjAZd:1q`VkP%8orE?_8\<c$G:=?%^E3Q_LJ<QJTagUY^##`..).T]90C
@Pa.O4b>!Z(pb!I,%o6.X:GGeX^^!j%&^.N\sGJ_"c6"c"$U33,j`dqg>]@doLqkfbC"m7F0k!kbC<un=W3h!\f#]oda9P\:W#e#Ka8?m_Cmkd"YWp.,
&YQYP&NE@Bg>?LVt1@'K6_]%@2!'%H?kj-AK)#K`6fr_6&bVRGR*2l%oqcHmJlRFY)B;/C>.ZpC'Op3#-a8">PPJ()X1RMPe'E8%pT!$N(\SsrdP4]&S
O5agH(I14'])T>f;q!io(_pF,RL53T9n1oQY.?PTXGCfbo1^3q;M;s+eege2QR!nuH<hTLZA-FH"%Wpl=uDEX2h>a(^Gd<pbDpX3N-2Dtr=;9:)ZR;V*
US,]T&\-:6YoDF3$:dLD[bc>G3^l]]hLo,;OI_^*u3Z*Q8M3DcYQZL>8p[O1=6,K"4]Tu2Q\3F+W8G_<P4e)N4Qa^#njARj_jn\Yee>%J(]7%a]ZfIE8
#aKsa)5#P60_dgR3g=AecSat#>Uc!kdNV]Ko2&f*c\!mi^co4Z8]4tUuQgEHZ80"1Nq/Y1M0FK@Co'=#%,Dt7)n-/ac,/&V#jLA9p,%;#Tj*+DS(Vh,B
qns'j@X1!0XIH70-tXtGWL2g.Li@X4dtIHua7Mtn`>Z(3.H,^_:p>nHZW]T5R<<OBYVup?8'H.8+/2<;QRb0$<XEa8*[4,nJaM#X_ZJP:oZRlA#qHmEJ
n];Phnlt<1l!hS&cSL5]$uki$+n)TeJ.MZ]UYT_d)$pfBM3[qg:7'R&U#M^`%)%FouJ+tC+a%Ro25'a\GY:Kp;2nR"F/Vjg+tLmiAD'Qo*b\N(7RH"8B
u$Amm*k11AQaXE&/^_Z=@;34,?')Gcf)SG_8m'nI=E+He<DOa)QR2D8Bq+Tlr`7)2"e/^I-l)6DV"U_3L&(>$uHUbQe:Bm<WZp0Xt3;3CgoQ<WO&81.`
buKZC$aUm\'aV<]:.2u_$t/#Q+Q\np/fCsm%Ur7T3c\\<AUJ\gD`]7a2_s.>X/+43M4L.IjUg!lBS4?ofL]"#Y.#QP8_#V]Z,1X5pKQG)b<ndqPP:VI%
Bl0SF7=5*O'k=JB00oPA8d:>,m0?&/6dg2toLO+A=(&RFl2]Q%nr[D?No`XhANt@qZ_9cXW"Nt/TD9nr4Hu@cQi:V;:WI'-Igl?eL+/TNa\or-1^Ge*<
Fm<4I`E3uPV^:IbPhZO27(#07YYbqGG5/t(3s/g3'5t7#!>ml]67$?6Z7U^OIf\iM^n(!4%'D7'+nLJL+E<40Ak4F@E7XY<$WF+u@MDP88U[`ek\l6D/
>2\`_^AkeUc0)/hqUhY\OI)@H$h,m#h`i9-\ZH8nBJd8ln4qikio-Aj1['ng)TcgfDd/@L+aKr6s7aHAmVd?!GJ?"ReS.)9FjNS9(n)tC87!>+'Zj)I1
rpo:Wc.ALMY1EHQDJbPLjb10nSi\V[K^NQX#g9QsW9Jn/GcnPF&Rid+IDOGBS28H^$Cr820MpaO2qGMDE'hVg5(l*#F`lfb&18(pn^A<NPB@3l@3gaJt
'bUEZE0g>t`YG#?e3,g+p^fp2k]!+\3:`$G2EFj>)YjE.RrDhs&UZN:pEW[6(Lp#5*sTjEX!Z3^4/!fU>AO6_G`nic-pF^hH0%1<M_-.+I6.Zhdj/tU[
T8VgQ):E2heq7S+_5Y$RDs5aCM:$E.Bn9NTX']&&gGWit#qIljA7&m'?.r1UKVQDtc@[0i^Vnb[t$h4;je0U#-\:ch7IWj=s`]\]Y7j%PBAuP[d?b)a(
2r#$@c@9S^^SE[)+s)^H_D9f0W'S\E=_aWt5$#1'<fG$am[Z>@[W*=BKs&+&bddSF/l[uD+pWEU^n33CXJV#:*[AZt.-#tRe#Y.b^e\9=l_YV5W&l`\P
tp.*d>2S:V6s3Wgji5Yp(tm%%(>ii61i%!Ue;tWs)QgD6&W.k%dUBK""`,sMgK$8pf6#I-FZ;2LhU29F%k\SgFEnmJk&H\'aN,i9u%+RZKt$eZ5_^p^7
RCVlPB\nLTQT#%RdY)UgZUDja/))0S>Z(dl]JOTc+`kO!rLBi(.,)S]E&T<\kn%I;2HWC(MH5Se#9T!f`1..ig`r0kEtH#lChE6>"KY!,J6=<i+D.0TD
p,>UNHe'?Qc2YdUS8`3Z"`^"E3.dsr_J3U[4&!LBAd)++(`^T0f065CN7e3C4-n7i9GMS'50jNOts+SP)'MHQoo$aT&9>,APsP$Jc\b6GQu+:d37%ch9
LZ2=#P`;3U.rf,J$?RkTZ#MV$'f+\Y\Z*+t_Z:eS#$tlcg58]'D+`hP)6Fi*.8O-'A^FKlY41'_>SX9s7$<i"&?[kB#N"7Xfm5B>T?"</73aa]R,"l:e
SBM65Ris]Q^HP7-.Qk$]/i4erX/EI8aBrrB?F/.(MJ[GBWr"U["EhW0pM,j=QXht+bUE+jJ_WN'Z-[%Cbei\T462gLKV=onOXZjVbkglRNbH<>iaEluZ
E_j0=cKN)5_97+S2qRpI&aYJebDlJ``c.ubCUMnhSBu%:XYkrK(<p[I)uATcDl6CGAUKYUZ5%M(=3sV_ugb[_mss_SiHUY/:!i0d=A:s=(Xdt3eE$nYg
kAJbZ7PA=)8,l4",!Z`Tf"6:7,q;%`4_:1lHL0?c$P()@4g"lZ,kRX/i\`.ecTO=];p)HGXR-Ak@S^3'kLX5[-HF"$%FO"'/Q:EV@5sGJre:O85d_6.O
]5EM%Xed4:&p3\F]2l)78&OaMpqQVA2h3c<XI*ZTjF@)CT7]-#3[rPtAE)a61-c5)81,"D^gUWNBOLO.'t8?`ZFN^!nri;-7iFb>cPZuWRJ#8<F-n8ZP
s[HV)j=B?QCaFZj9KVbG^.#H[(%,VKqn5Dg\o#PohECC@$N#9!p"BYe`G3Dur<P^6.G)RT7hQQ#nAVE6#G+?&2"j$Cd*ga`X2h,`<mQ^X\r^GQ.oIeL^
$n,cu,6o[tB3`/W_XYJb7)=EB"NY;q!0sekD*kLi:47s&I_G,'7XT7;oh(AC;N55[G>Z)K11VXZbED^I8_hU9,JP'(72Z^]R^'Yj9t0(uD&=@Ci^.t_,
&GOJp?_jXX-Y8?'CX!S44oYNk$HX3#fe8?dKWc^G)"1P&r7+8K/=>-*-D*Q@9_MkZFOd&MnK9f9t@jQ_$bdrEB:o1-6^[l6K[HIoSQdX4Siug_g7h#@P
\eXjn[JH=/:,naV:7"3//$DqOP)_55/Pb6(!.#&@/)s7J:UnnUWde51]s!j<qABZLs@(=\cb[Ne_s[oiO/E?HG$9kC54>DodIaCCqPoZkS%!\P"".WMI
7T6V/^3D%ogN'MZG<n<pB91mVi>KJfG<+TpnR_SdtZ6bbJ<M`.b%/jaEH3?NlL7m>khf6)`dNSE9W`iObDnO607E[8b'"UeNq,pZdo<6Vc*fBg&m5u[7
%;m!99NiTErSinTc'6FUhGng7EAch0cF[c=qF^Bf3E6/*Gp2L]b.,>0JWL!u+rA*cYGc"!>pAeOe[bBdu4hoAR:R5Ht&s5%O!H33_:7YWge:*RqRNcqo
-@tUfp.n0-HFMb0X$@l!/MBS29*r5RQse=&C#nD*nLqOmlV#rR8pg$o)4G!.R/V*(BS$,q;?l%HgW:n_/60c+Cu3hsd!R9]>pmM3kIl;e+jgt(6ZH+=9
6W*)`/#UQYD/B";cO8e8aO+]2^9t&Gf!3+h*hQ`*s?k"RG4tWQ;s.H\a#.68gH)T%&Mpq"=Iu+JVZo3;hsIkL$rKfC>ZQF,5)f[&MMr?G\5_a/QA)0=A
r>G)@YG<"^3Y',R`%$6Iu9f1^bk55.F%Z#F,`(D\SNL(CCA0TE*?enc0Eih1Ug!?b\L3@$*m4^BRKbI&h0+'ucSb=O$kH,7/4E@7.S9)u;9dn^.2SR)/
?mfLZ3*W-cb-6?gpZGO%UPCX4'Q`dAj7THe`OMUdFj=cP69I05FMdkqrA1L]!-AUu;V\RE8`5C=]i\Ud$:p+VF_*83U:o.N20K*-\SaN>n>1KS$A]V1o
"JC.iI._*ONrK`%tOJ87:6\sc'pi68t$5m,#*8)8$M<ts$IHT*B[oQr$2N91f8,MEF]L^2"Nh)*VLKRR&cKq\j,L5Dg=+C8EHRe[8C5Sng]:(83?=25l
5eeh/h7Buf0!EagVN5]YR"[%3i!CdKSiQk)?Y.Zi^QMUk]K9[?%ur?AnKQ5lV+j^JYrRn]INh5V8e%2c71[#Tq'((n#0S4@)Sm!o3@,">TfcmS")`O#_
\!c#e"#ua%.=Q$M=o5!<Okg*H]Td)2qoTnNn:(O;'r*TTsYgFSbj>AkS;'IjB14D_ck=.h?0i/QXs'%5I'Zk:;4p;(m8/>+]#G$mgpKO[=r%Y@5A7PHL
@Y&aFurl2"_d<X@`?6H27)0r4>MFDuPBa_Bg,"/qCLQCCu?RIfE]\ioI56eRIr-cDKVhG.Z;jjrd@A`LApWZ9^7!cu9!ZBc9Q0/X:#]Zs_E>Hau#6`0Y
YN1T,,0D"MF*:(U`S\<N;7gK$l%&lq]o5glY&r-37nSAISQ>\h6]c1%SWEm;'-$bGQS!!8Cq5ik:rR,<1]hJ<WJ/hf>kU>ghu6Ku>9LUng5EU2a]&QiQ
N*I0[aMNKA7KNHu-`DXr=/WgYKNF(5D"%3*ks4Wr!j-3[@s2"8PM/5?eUJt;PV&T:u![O[Y[A'!8[2O>]rF,1j/G=#f_XBB$@5g!/Nq"m8P@-Doa%WoE
J%qnMk3G%Ki=s>n[1@,^@>j\8FEhN0`om\)D0qE:R`HqPJ4V2sGJQF,mfou/XJaY?rc[UV'\!tti]K/e%3;p7@SNFf[s'7\]4L4kbgc8r$2#b)fj<"rX
3o1Z^c;DqS!6qW$2SYp!!/0?QbEJ#:7ZhqZ,C;P!WW3#!!HG.'''
	exec(lzma.decompress(base64.a85decode(_SRC_B85)).decode("utf-8"), multiCMD.__dict__)

try:
	import functools
	import typing
	# Check if functiools.cache is available
	# cache_decorator = functools.cache
	def cache_decorator(user_function):
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
		def decorating_function(user_function):
			# Create the real cached function
			cached_func = functools.lru_cache(maxsize=None)(user_function)
			@functools.wraps(user_function)
			def wrapper(*args, **kwargs):
				# Convert all args/kwargs to hashable equivalents
				hashable_args = tuple(_make_hashable(a) for a in args)
				hashable_kwargs = {
					k: _make_hashable(v) for k, v in kwargs.items()
				}
				# Call the lru-cached version
				return cached_func(*hashable_args, **hashable_kwargs)
			# Expose cache statistics and clear method
			wrapper.cache_info = cached_func.cache_info
			wrapper.cache_clear = cached_func.cache_clear
			return wrapper
		return decorating_function(user_function)
except Exception:
	import sys
	# If lrucache is not available, use a dummy decorator
	print('Warning: functools.lru_cache is not available, multiSSH3 will run slower without cache.',file=sys.stderr)
	def cache_decorator(func):
		return func

version = '1.40'
VERSION = version
__version__ = version
COMMIT_DATE = '2026-04-13'

SMARTCTL_PATH = shutil.which("smartctl")
DISKUTIL_PATH = shutil.which("diskutil")
IS_DARWIN = (sys.platform == "darwin")

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
					mapping.setdefault(tgt, entry)
			except Exception:
				continue
	except Exception:
		pass
	return mapping

def parse_bytes_from_diskutil_size(value):
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

def get_statvfs_use_size(mountpoint):
	try:
		st = os.statvfs(mountpoint)
		block_size = st.f_frsize if st.f_frsize > 0 else st.f_bsize
		total = st.f_blocks * block_size
		avail = st.f_bavail * block_size
		used = total - avail
		return total, used
	except Exception:
		return 0, 0

@cache_decorator
def read_discard_support(sysfs_block_path):
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 'N/A'
	dmbytes = read_int(os.path.join(sysfs_block_path, "queue", "discard_max_bytes"))
	try:
		if dmbytes > 0:
			return 'Yes'
		else:
			return 'No'
	except Exception:
		return 'N/A'

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

def read_size(sysfs_block_path):# -> tuple[int | None, Any] | Literal['']:
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 0
	sectors = read_int(os.path.join(sysfs_block_path, "size"))
	return sectors * 512 # linux kernel uses 512 byte sectors

MountEntry = namedtuple("MountEntry", ["MOUNTPOINT", "FSTYPE", "OPTIONS"])
def parseMount():
	rtn = multiCMD.run_command('mount',timeout=1,quiet=True)
	mount_table = defaultdict(list)
	for line in rtn:
		if IS_DARWIN:
			# macOS format example: /dev/disk3s1s1 on / (apfs, local, read-only, journaled)
			match = re.match(r"^(\S+)\s+on\s+(.+?)\s+\((.*)\)$", line)
			if not match:
				continue
			device_name = match.group(1)
			if device_name.startswith(os.path.sep):
				device_name = os.path.realpath(device_name)
			mount_point = match.group(2)
			options = [x.strip() for x in match.group(3).split(",") if x.strip()]
			fstype = options[0] if options else ""
		else:
			device_name, _, line = line.partition(' on ')
			if device_name.startswith(os.path.sep):
				device_name = os.path.realpath(device_name)
			mount_point, _, line = line.partition(' type ')
			fstype, _ , options = line.partition(' (')
			options = options.rstrip(')').split(',')
		mount_table[device_name].append(MountEntry(mount_point, fstype, options))
	return mount_table

def get_blocks():
	if IS_DARWIN:
		# On macOS, enumerate /dev/disk* and /dev/disk*s* nodes.
		block_devices = []
		try:
			for entry in os.listdir("/dev"):
				if re.match(r"^disk\d+(s\d+)?$", entry):
					block_devices.append(f"/dev/{entry}")
		except Exception:
			pass
		return sorted(block_devices)
	# Linux: get entries in /sys/class/block
	block_devices = []
	for entry in os.listdir("/sys/class/block"):
		if os.path.isdir(os.path.join("/sys/class/block", entry)):
			block_devices.append(f'/dev/{entry}')
	return block_devices

@cache_decorator
def is_block_device(devpath):
	try:
		st_mode = os.stat(devpath).st_mode
		return stat.S_ISBLK(st_mode)
	except Exception:
		return False

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
		match = re.match(r"^(disk\d+)s\d+$", name)
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

@cache_decorator
def get_sector_size(sysfs_block_path):
	if IS_DARWIN:
		return 512
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 512
	if get_partition_parent_name(sysfs_block_path):
		sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(get_partition_parent_name(sysfs_block_path)))
	sector_size = read_int(os.path.join(sysfs_block_path, "queue", "hw_sector_size"))
	if sector_size == 0:
		sector_size = read_int(os.path.join(sysfs_block_path, "queue", "logical_block_size"))
	return sector_size if sector_size else 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
	if IS_DARWIN:
		# Per-device throughput is Linux /sys stat based; return zeros on macOS.
		while True:
			yield 0, 0
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		while True:
			yield 0, 0
	rx_path = os.path.join(sysfs_block_path, "stat")
	start_time = time.monotonic()
	sector_size = get_sector_size(sysfs_block_path)
	previous_bytes_read = 0
	previous_bytes_written = 0
	try:
		with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
			fields = f.read().strip().split()
		if len(fields) < 7:
			yield 0, 0
		sectors_read = int(fields[2])
		read_time = int(fields[3]) / 1000.0
		sectors_written = int(fields[6])
		write_time = int(fields[7]) / 1000.0
		read_throughput = (sectors_read * sector_size) / read_time if read_time > 0 else 0
		write_throughput = (sectors_written * sector_size) / write_time if write_time > 0 else 0
		previous_bytes_read = sectors_read * sector_size
		previous_bytes_written = sectors_written * sector_size
		yield int(read_throughput), int(write_throughput)
	except Exception:
		yield 0, 0
	while True:
		try:
			with open(rx_path, "r", encoding="utf-8", errors="ignore") as f:
				fields = f.read().strip().split()
			if len(fields) < 7:
				yield 0, 0
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
		except Exception:
			yield 0, 0

ALL_OUTPUT_FIELDS = ["NAME", "FSTYPE", "SIZE", "FSUSE%", "MOUNTPOINT", "SMART", "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD", "READ", "WRITE"]

# DRIVE_INFO = namedtuple("DRIVE_INFO", 
# 	["NAME", "FSTYPE", "SIZE", "FSUSEPCT", "MOUNTPOINT", "SMART","RTPT",'WTPT', "LABEL", "UUID", "MODEL", "SERIAL", "DISCARD"])
def get_drives_info(print_bytes = False, use_1024 = False, mounted_only=False, best_only=False, 
					formated_only=False, show_zero_size_devices=False,pseudo=False,tptDict = {},
					full=False,active_only=False,output="all",exclude="",
					filter_patterns=None,invert_match=False,match_devname_only=False,timeout=None):
	global SMARTCTL_PATH
	global ALL_OUTPUT_FIELDS
	if output == "all":
		output_fields = ALL_OUTPUT_FIELDS
	else:
		output_fields = [x.strip().upper() for x in output.split(',')]
		for field in output_fields:
			if field not in ALL_OUTPUT_FIELDS:
				print(f"Ignoring invalid output field: {field}.", file=sys.stderr)
				output_fields.remove(field)
	if exclude:
		exclude_fields = [x.strip().upper() for x in exclude.split(',')]
		for field in exclude_fields:
			if field in output_fields:
				output_fields.remove(field)
	if not output_fields:
		print("No valid output fields specified.", file=sys.stderr)
		return []
	output_list = [output_fields]
	output_fields_set = set(output_fields)
	macos_info = {}
	if IS_DARWIN and {'SIZE','FSTYPE','UUID','LABEL','MODEL','SERIAL','DISCARD'}.intersection(output_fields_set):
		macos_info = get_macos_diskutil_info(timeout=timeout if timeout else 4)
	if (not IS_DARWIN) and {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result = multiCMD.run_command('lsblk -brnp -o NAME,SIZE,FSTYPE,UUID,LABEL',timeout=timeout,quiet=True,wait_for_return=False,return_object=True)
	block_devices = get_blocks()
	smart_infos = {}
	for block_device in block_devices:
		if 'SMART' in output_fields_set and SMARTCTL_PATH:
			parent_name = get_partition_parent_name(block_device)
			if parent_name:
				if parent_name not in smart_infos:
					smart_infos[parent_name] = multiCMD.run_command(f'{SMARTCTL_PATH} -H {parent_name}',timeout=timeout,quiet=True,wait_for_return=False,return_object=True)
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
		pattern = re.compile('|'.join(filter_patterns))
		filtered_devices = set()
		for device in target_devices:
			match = pattern.search(device)
			if (match and not invert_match) or (not match and invert_match):
				filtered_devices.add(device)
		target_devices = filtered_devices
	target_devices = sorted(target_devices)
	uuid_dict = {}
	if 'UUID' in output_fields_set:
		uuid_dict = build_symlink_dict("/dev/disk/by-uuid")
	label_dict = {}
	if 'LABEL' in output_fields_set:
		label_dict = build_symlink_dict("/dev/disk/by-label")
	fstype_dict = {}
	size_dict = {}
	if (not IS_DARWIN) and {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
		lsblk_result.thread.join()
		if lsblk_result.returncode == 0:
			for line in lsblk_result.stdout:
				lsblk_name, lsblk_size, lsblk_fstype, lsblk_uuid, lsblk_label = line.split(' ', 4)
				if lsblk_name.startswith(os.path.sep):
					lsblk_name = os.path.realpath(lsblk_name)
				# the label can be \x escaped, we need to decode it
				if 'UUID' in output_fields_set:
					lsblk_uuid = bytes(lsblk_uuid, "utf-8").decode("unicode_escape")
					if lsblk_uuid:
						uuid_dict[lsblk_name] = lsblk_uuid
				if 'FSTYPE' in output_fields_set:
					lsblk_fstype = bytes(lsblk_fstype, "utf-8").decode("unicode_escape")
					if lsblk_fstype:
						fstype_dict[lsblk_name] = lsblk_fstype
				if 'LABEL' in output_fields_set:
					lsblk_label = bytes(lsblk_label, "utf-8").decode("unicode_escape")
					if lsblk_label:
						label_dict[lsblk_name] = lsblk_label
				if 'SIZE' in output_fields_set:
					try:
						size_dict[lsblk_name] = int(lsblk_size)
					except Exception:
						pass
	if IS_DARWIN:
		for devname, info in macos_info.items():
			if 'UUID' in output_fields_set and info.get('UUID'):
				uuid_dict[devname] = info['UUID']
			if 'FSTYPE' in output_fields_set and info.get('FSTYPE'):
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
		device_properties['NAME'] = device_name if full else device_name.replace('/dev/', '')
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
					parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
					device_properties['MODEL'], device_properties['SERIAL'] = read_model_and_serial(parent_sysfs_path)
			if 'DISCARD' in output_fields_set:
				if IS_DARWIN:
					di = macos_info.get(parent_name or device_name, {})
					device_properties['DISCARD'] = di.get('DISCARD', 'N/A')
				else:
					parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
					device_properties['DISCARD'] = read_discard_support(parent_sysfs_path)
			if parent_name in smart_infos and SMARTCTL_PATH:
				smart_info_obj = smart_infos[parent_name]
				smart_info_obj.thread.join()
				for line in smart_info_obj.stdout:
					line = line.lower()
					if "health" in line:
						smartinfo = line.rpartition(':')[2].strip().upper()
						device_properties['SMART'] = smartinfo.replace('PASSED', 'OK')
						break
					elif "denied" in line:
						device_properties['SMART'] = 'DENIED'
						break
			#size_bytes = read_size(os.path.join('/sys/class/block', os.path.basename(device_name)))
		if device_name in tptDict:
			try:
				device_properties['READ'], device_properties['WRITE'] = next(tptDict[device_name])
				if active_only and device_properties['READ'] == 0 and device_properties['WRITE'] == 0:
					continue
				if print_bytes:
					device_properties['READ'] = str(device_properties['READ'])
					device_properties['WRITE'] = str(device_properties['WRITE'])
				else:
					device_properties['READ'] = multiCMD.format_bytes(device_properties['READ'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
					device_properties['WRITE'] = multiCMD.format_bytes(device_properties['WRITE'], use_1024_bytes=use_1024, to_str=True,str_format='.0f') + 'B/s'
			except Exception:
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
				if formated_only and not device_properties['FSTYPE']:
					continue
				device_properties['MOUNTPOINT'] = mount_entry.MOUNTPOINT
				size_bytes, used_bytes = get_statvfs_use_size(device_properties['MOUNTPOINT'])
				if size_bytes == 0 and not show_zero_size_devices:
					continue
				device_properties['FSUSE%'] = f"{int(round(100.0 * used_bytes / size_bytes))}%" if size_bytes > 0 else "N/A"
				if print_bytes:
					device_properties['SIZE'] = str(size_bytes)
				else:
					device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
				output_list.append([device_properties[output_field] for output_field in output_fields])
		else:
			if formated_only and device_name not in fstype_dict:
				continue
			device_properties['FSTYPE'] = fstype_dict.get(device_name, '')
			if IS_DARWIN:
				size_bytes = size_dict.get(device_name, macos_info.get(device_name, {}).get('SIZE_BYTES', 0))
			else:
				size_bytes = size_dict.get(device_name, read_size(os.path.join('/sys/class/block', os.path.basename(device_name))))
			if size_bytes == 0 and not show_zero_size_devices:
				continue
			if print_bytes:
				device_properties['SIZE'] = str(size_bytes)
			else:
				device_properties['SIZE'] = multiCMD.format_bytes(size_bytes, use_1024_bytes=use_1024, to_str=True) + 'B'
			output_list.append([device_properties[output_field] for output_field in output_fields])
		multiCMD.join_threads(timeout=timeout)
	if not match_devname_only:
		if filter_patterns:
			pattern = re.compile('|'.join(filter_patterns))
			filtered_output_list = [output_list[0]]  # include header
			for row in output_list[1:]:
				match = any(pattern.search(field) for field in row)
				if (match and not invert_match) or (not match and invert_match):
					filtered_output_list.append(row)
			output_list = filtered_output_list
		elif invert_match:
			# if no patterns but invert_match is set, return only header
			output_list = [output_list[0]]
	return output_list


def main():
	parser = argparse.ArgumentParser(description="Gather disk and partition info for block devices.")
	parser.add_argument('-j','--json', help="Produce JSON output", action="store_true")
	parser.add_argument('-b','--bytes', help="Print the SIZE column in bytes rather than in a human-readable format", action="store_true")
	parser.add_argument('-H','--si', help="Use powers of 1000 not 1024 for SIZE column", action="store_true")
	parser.add_argument('-F','-fo','--formated_only', help="Show only formated filesystems", action="store_true")
	parser.add_argument('-M','-mo','--mounted_only', help="Show only mounted filesystems", action="store_true")
	parser.add_argument('-B','-bo','--best_only', help="Show only shortest mount point for each device", action="store_true")
	parser.add_argument('-A','-ao','--active_only', help="Show only active devices (positive read/write activity)", action="store_true")
	parser.add_argument('-R','--full', help="Show full device information, do not collapse drive info when length > console length", action="store_true")
	parser.add_argument('-P','--pseudo', help="Include pseudo file systems as well (tmpfs / nfs / cifs etc.)", action="store_true")
	parser.add_argument('-o','--output', help="Specify which output columns to print.Use comma to separate columns. default: all available", default="all", type=str)
	parser.add_argument('-x','--exclude', help="Specify which output columns to exclude.Use comma to separate columns. default: none", default="", type=str)
	parser.add_argument('-t','--timeout', help="Set command timeout in seconds (default: 2)", default=2, type=int)
	parser.add_argument('--sudo', help="Run commands as root with sudo. Needed for querying SMART info.", action="store_true")
	parser.add_argument('--show_zero_size_devices', help="Show devices with zero size", action="store_true")
	parser.add_argument('-D','--match_devname_only', help="Change filter pattern to match just the device names instead of the full line", action="store_true")
	parser.add_argument('-v','--invert_match', help="Invert the filter match", action="store_true")
	parser.add_argument('filter_patterns', nargs='*', help="Filter pattern(s) to match (e.g., sda, nvme0n1p1, btrfs). If specified, only devices matching any of the patterns will be shown. Will prioritize print_period first thus if wanting to filter a number and do not repeat, append a 0 (zero) at the end.")
	parser.add_argument('print_period', nargs='?', default=0, type=int, help="If specified as a non zero number, repeat the output every N seconds")
	parser.add_argument('-V', '--version', action='version', version=f"%(prog)s {version} @ {COMMIT_DATE} stat drives by pan@zopyr.us")
	try:
		import argcomplete
		argcomplete.autocomplete(parser,always_complete_options='long')
	except ImportError:
		pass
	args = parser.parse_args()
	tptDict = {}
	if not args.print_period:
		if args.filter_patterns:
			try:
				args.print_period = int(args.filter_patterns[-1])
				args.filter_patterns = args.filter_patterns[:-1]
			except Exception:
				pass
	multiCMD.set_sudo(args.sudo)
	while True:
		results = get_drives_info(print_bytes = args.bytes, use_1024 = not args.si, 
							mounted_only=args.mounted_only, best_only=args.best_only, 
							formated_only=args.formated_only, show_zero_size_devices=args.show_zero_size_devices,
							pseudo=args.pseudo,tptDict=tptDict,full=args.full,active_only=args.active_only,
							output=args.output,exclude=args.exclude,
							filter_patterns=args.filter_patterns,invert_match=args.invert_match,match_devname_only=args.match_devname_only,
							timeout=args.timeout,
							)
		if args.json:
			import json
			print(json.dumps(results, indent=1),flush=True)
		else:
			print(multiCMD.pretty_format_table(results,full=args.full),flush=True)
		if args.print_period > 0:
			try:
				time.sleep(args.print_period)
				args.active_only = True
			except KeyboardInterrupt:
				break
		else:
			break


if __name__ == "__main__":
	main()