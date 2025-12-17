#!/usr/bin/env python3
# requires-python = ">=3.6"
# -*- coding: utf-8 -*-
import argparse
import os
import re
import shutil
import stat
import time
from collections import defaultdict, namedtuple

try:
	import multiCMD  # type: ignore
	assert float(multiCMD.version) >= 1.42
except (ImportError, AssertionError):
	import sys,types,base64,lzma   # noqa: E401
	multiCMD = types.ModuleType("multiCMD")
	sys.modules["multiCMD"] = multiCMD
	_SRC_B85=r'''
rAT%)=o\O*k16n/!WXAE)uos=&C4J&i'O+R$XE`ELdFUh,;[5]%l=/aQgL]knEMJj2Td\)1[`bH(.0)JfPPs3eIh*#BVY2@n9=XkOcI@DKhS;S&As]ZP
9!<g%=C-.%/0Ih=#O/1YsCX1=T[AZ%Ln2XNTcW'0qer&.B;*#ARBc\-147SBU'CMdPY2@.iA,rhT6fbA1A5mK8)nUX%5ViLm\+h]N.Y8':Wi2TuHDUjm
gM*:^FDY(CBm.A+qC2`>1]:cu9K$D]b2kWFgR^g'\i[gIC^HTuYaPXgHFSl9XXX#NRC9jbAE=,?4]cN(PrihO$tYZ5@E3%)(:D7Kje-MgI>dc#sSt@[T
Ttq8j:Q5]/9!M4T1N^.m)GOZU'&klU64#Ct]R2c'j%]bNY'nc[-Km$mOCK0X2WNDiHO,ij&mFn[24S&YQ]"6J@HVr&2"JG^mD;3E,d6A/SYlVM^BOc6D
-fMC/K#(?WER:77uQ)c1lH1,)!J'u+*ie4Dp3<!>;6JsY1$!)E`oe@oH>0hs0#Y6;NEUXCq2qgb]@*VI'W#/M!$@Z2h=Y<&o:1ML!meO7BF"+BTT*rQ#
aISaeS_ig`G0;KfPb1>\?2#bI_AgO\=&M;pk-(2XfD"2bX:2E/7.j-fKqM"9>lI.Tb_fLgF-O9(i$Q!CT40ZQ2@S"Af=,2!k"[rAmm'iR70"QBmNdGd!
FqR^H`cTtM*BC7Ze/9<RL@3,)8Y#M!\3`8L5sdTZV8R_1!ig6E%@(O9TP"&hW<eA09A:$"dm8ME2/o#AV@JeVZ^q7C87sISO2VoW>Gb'<)VG'O6Gknm@
/+Jcq@")A)N%7*Am,n-1+j)fq63^g>:(,WAr1:1)3rRlS=?jTm+Q/It`&(Boe,Dh\QbJ]kr#8:rQNFKUg3S'mRD&%06c"CD\eBBF@*ob&4inbj;:;-!A
ObH_7"\?%5sAa#:?ra*AQ>b&r("]!a0RN3AU\,Sclo*GGdK!D52c^Eko\MHgL)E8_>X#,1N3STW@O&p)<)3A@:8d"@6@[+Kii<`-)FTj5=f)7g@`Xqe+
3W6PYh?G[NR7>Emu0hHq8pk/+Bk)RZX;RX&rNMWD<^^\;Y%>`@R#9H4e,%#2J3(kt21!Y;K0eqZ*^d8gD>Bgdm^_$2ikFsEWr9H\j)Ib_op9\W9T(R>\
Q*7s8L@jPoF_pLM1(QfN'0Ja@)HBim2"=mH,X/upcHr[AL_NmB"RdY\\V,!Nlr;Y<mkk%gH"V8]P<.<NGfo@.8W]+ui9Lc-/n3e%Y3iW5J2Hg@Dqbs0(
=[f>3hO;SDHZg6FftC6Jf.YPmkQi3N@Vbt(_H<K*ta4s2j?h'-,P*7WFY*gUun$[jXi(kN72+WD3=Wtc[(8ShQ<Js-ft]^Cu_89kY`\WiKgrfXm>,g"]
pm,@Lr?o#2FrmM1\t''uDt>>*0t2Cp';b?VQ\#UtU,.q[R(@GD`VQR.!Do:jj0f(gN\iP?EFVE8H7I/WT!G8,hE>A4:['*`8A!.^We[Vp)Q/U#gFj&!m
u5Y_"CVd5(VV"S&*P)[8qrAl9=NK-QJi-b,ImMopqgV"/=djP+7/eO'A[5h%bhEAn*u-Im:Imiq@c6$+.r_F`+7\ZL3(SJ2b.jNHSDn&C-`qUuGFBMm-
L&RO0j#6S^JOO/X#)m4D\c`'X2FBVriq3?=E:A$76/glK/#i-I34(D->+*[K**^n5i7>bV3"iFJE+fU/QjP!^5-1@=KB]!$4;2>'^Aohn8XO*M2ZkGSB
X-?+R"f1u?H].$c,(]<e-MN`D:%^%]8?Kp7pZ.4NU\LR.7W+;`)"*)7Ki-9BAg!jT`3hZ+=IDCn;n!JLY1Tqb[BqkhFAod$Kr0:/F=*M+[&IOo-ksdZn
MOBgrARuQE^?`fQumE&B_Dn75)>KABeF&GK>jsNdV,;TPol.&b6qc4HlE&=4Q9oF'U"^@9<aa@AWcpJ'nX-j7YLQC6b@!^cUF[jAOnj^ksj7HRi!pFid
a$+//GNjIh(u$+gXZMMo.W.4C2Dplsl3<_3c<8\R$.K)7lF`9G1r$O`b.RciN^r!<M=m$dU(3AkWtuJ5_+:iW*euY2_;I?3uZ[Th?Zm1\"1JhW<APDHe
1Dd6;P]<VF2_PsQ[5a6i9TWF#q.&"k?3[B*A-+j"OJMRf;*h"n!!lO(uuqUZ0Ur2p>Kg#OT)G:]gB=cEAGkpn4MNR!-6"LG\_MF!k@=#IPD/ZDgM7=^;
7B\Q>'rMC=9-5o7"jFni>qO[csf^6ndRdBtoK9hShnTAU#"l"QScZGYcf6g<S"je./IQ60ITR3VXln,Z[@8J\DW%sWiDU7tsGCaduhcJmBc8VBm&M3Fk
5PLKYd<$ma!F73D2/k/T15W-c\]b\0Uda/#CLt'AH`rUJDHg35!0f-9R=g*[,AAa1O79:6fnB1'fP5F]%QHA5_lgdHLTVQ<.FQ"H@bqD2T^s)HoY=bZL
SQK1H0*+\`L%JZ=fR%kY,,1KHcH@b=k&_5N)D<85uK"5fY:U9a@K,*/XQi`rrIM8LOISo;ickU'(?h_IT;4lf'SL58i[Psnl0iGheGV7o/5uSD8EQgHb
b5IA1"K!"jlrHW!,\(:gcGWUQ_s.(WUQ2`h>:<>qu<WJ!gU>:UQm.G9E&(iY383Ojg-NWpM@e0Xog&k_/ok`Cj'%)<?ig'K<D%-R?qZ\=0<fC6[l)Fq[
aH$Z#2>0=O1i_+gWmfhMui2[D\rZG>uP/_TX@I=W5DZ2mKjfe7Th[d;W9:n5Xf*eeH3fHg$CeLFl)UDGU/9ip@d\HYAK=]7JfhZH@6.7k.+=^8.=NFW+
$VWB_[@47iH74]P4LZehRaHLN>ZgA#1#Sap6'QX]W+cpb9W\0]_:h*DnbqFrWGW:E%)tCA5#0,_'=f7hZ]btG?=raDC>Q6];cP?bsW9hS;m^ZltHCS';
A8$CoShZIKZe1c%`GnsM"-9i$ER4-99)C$U5+R^g,;R8M'+pEc(4V.MO[OHK_oIQSK=`Zt5!q\KQ8TYAj/_+VI<\@AE69dfpAL4]l6.Z77#o*:d)3!mk
11.%iVlTbYG9Q:hjoBJB%kSX"t#Phd9R@cYA?Ec5]u_mqr)!'"isjWO--MVQjoB,@MqO,U]f<lCsi\-e'IpD,>Br(=?E:33R.5>``JHnTZt-.$b-&jC0
)F,5a,ka_J2uZF[kF8b==4;m5Ap.R8ARVSM6VdTs,%[ggUONH?j;j*8U+D/JMW'G0:3TVDH'!["nMqBCdCJ;jE+&.%nY^5AX6[2>aq*@k!hT<tZWE(_o
[@HjJZ$"7[*]2sMbe!le7GoFbRBE(;5tCaDfrUtmua9*jE=AVO>9l8H<9`qi8!:L>I)3.]-k)/BN=oVN!r$-"bDW^Fh.ns`DfMp!<5`O_3Yfu;+dH<<%
pH?'k_g.0jbOh89I?"mpqT8Y?$A-I(lH3<X2WD"L!fBB6A?"da'@4&q5\$&mWppSiE0tkfYRoHG5ojKR,H?H5=j2]:h+],C"7Q*k`rD!_R%,U(K69hjc
:-!r^,uH9/?:;j9c;A1?H3#cn)gmnFeGS/R#r3th'nX(YX9j=*mW2<UID.XqH/T/r$O#3Z,1o"#;0I4[jXb?YmMRF_JY^$-5T^ci+BJM.*/JXTTa[Ee2
Z)[n&0SkulUa4Wju*LKR/kS9/7rGRP'G!ALQF$dQcPdTQHNMh3TboQ$\<Xu8?Qkrk^l/O(6_kn<i5gI=-c5K_j]-3ajs8`R\otSFu..5\W-sOJ^/+dD)
h7DZ-BaHFMPV9mbqnDCnX53\(qG1]Uq].gT\".-g+_Qs$V2aB&#,T=q2pV9*3=8K=)2jE?`Dp(-Z.j^(`J"Bh;N**)Hase]:RB$r"::a-!:S`^N*C%SD
Z;+A:Y!qdRkXXW384C4l6?mt;eEe^9<FF_Ie-Ot]NZN3^t>]i)r0&3?j&S-/e^NXPt%l^t.Tottg\:[MSkaX)T7haP,pl:C=]m%bA1"Y'/,Q<3Her<3u
jl^e>YMC!VsQB1.<buV3%qoRU%LL>+Rk@ATo[\f<OO=$+MmKD"_ha:2thsDXcr>cR_oZ2JYrlEKgNf*\&eg5_gE7)IBH+=D2LRX/';q8P9(=C#8]JPi-
NP%b\rN'=cQODrBoYF/hA)bcH&Zjsl#WCZf6[9.VHlpPP?fg`)jkHqZiH/oZl<R&D,31H8ZH!M9/Cg$sbYZ1k,LUTH8\WR2UJP">ZmD"K38k``ji`'#"
E-Rn_>%Fr8&nm`"Hmcr%]CBBiIQ"!@8qi5^UkoR+&<S`k9CUBORnC(H""'A>9gTS24N/*4_0C1TV&7]&UrO`1CXYU/NG<://?SM=mQJ#T-/<':0tjtCh
rD39&K&6'&k0Edt\If<6m7[e>ea:BVq+Y;T6]0YbOc+hqAmAkPOCNG,*;aJ,MI48+#sQ+#3^+aT`(;KBZ+94uZg#<KjCH^;3*<+?e&nT#/RpI4UZq,=k
*qAV?u"XCFS-Bh-`c5#ajkLJZL@kPW44I%#tc#j\t"^XpPi0PSX1XgA<Y4<\UmQ2FCl075Si:&h+u3LVq'md,hm\#f8;aBA:cTA&9V5IX-/H<f/b,iS<
.:-*&e)"IGRg1Zh1/P#CcS%eIc2t[?(/R;\0V/N"jaq%go,rn;]EhjWY5)1V],KYJKO_+WBEnALDqF7!+-.9cPa+\YQ`6I6:ca]NB_^7ep$P^&=ZbkaK
hb:?1.h4g;a56S#rfMXWZ-@ERhU5Sjhgb<7/bD%cKHZ=KQQoCJ\E%Caa>_r9g0f7(7E?9O?18-9"H)X.]Ce92^0Q9Gc:(!Vf=dR(V0J@_Fj)>a3Q,h'r
;/UcNp^<Eak][t(4qo<h,WVjEc+a&)d^e#-$KX':u*_M_jFc_l+P\,>snZf35<^ra,HpccqB55%pM@g3%WJ.9mj+($l_("Xo(hg.DMcD#Z1RVRCiY"d1
75aB:YM;.t:-EcD#l26k\P\RsQuc^/]3/e#"MCr<@r907^iW4mQD;66dJ19o"WD`S'`^82QB[KG,f!0T3j75Y;;3^ea[l]CIO-^@o^QmGdJDD#mFqU\5
7Cht9DHCX('uI84rKR-B/=q5XjOZ@L;=QK6`6n::hsA"uEQm[EFg.XcRrY+M.Kl]*m]`-n-@R)EMjfYK5ECT4e>mCsno5,iKS!d7G^EJ4GBL(?!^..$)
<S?F_*PTHop<V!:i8&r&5UVrq$a<G$R+&4k2]p>6nqX0jm?NrDF>BZV=T0!FmlD%2BQu_K]TW%gH:h%4YZqcb0:cracEi"),9tIA+Pnt'hZ-@o1SruG]
.ouX0[adm("!`ZJOu'p'21ik8S'9e=CDUoVr^6g8H!KNc<+VSrfK>MTlht^`VD!HW"Ri8\9CX9WTp`*_Sa^;F_DU>Y+B<glO#boY"CJJ"aB/r3d0ua<j
O3rV[IiLlOU=[k6`ep7,+:=Y3J;rJ+9PVm#%)1+)0Go!JQL34j(KW,%saG^EEnJ>QE\ha,s8MUa/5Pi_Zp!XbuJ5hX`'S_SAnSJR8q@.F-BCN@_fKE,j
@2+5IhSh%W)]1];3:*6ue7sBQG5q6?qRoZZ2)<Ncg0E+2i&mKt[]6RS'pD7l%-LMf>abN&&sF]9C+7a\s5lo[DWsa?mkP*`Ocjs-b>FVE!LsC]+h02G;
dk,"7LF=_$qHP"TN1X^XE6P+nRb`2Q6g'ri=$+,.ug`W"ZA%nSPcPS%Ro0DbPW8,=u2QnHMB\Z5GTnr"R>MU@s5=gbV.;&dHlHI2U-LBRiZ(Ch4V\,nV
5$T5+U.=eV7)[iThAM0-n/P)sHqm.b%^[)Q=PX)_@6oYd\O6W*Mi"o^EhPSt*PV4At5GYdRU4X=3'G=OALad&<GH[8"8n%O<;Vq-0q"[%?e`GUflU<.i
F->VUn!cfff)qHlRM8H^(<[_)00DL_2)gn?s(G:',/_6H@XCW0l<qlQm&)oU\eR=.++<@/gJqJD(7FfsQ0HV?([;Po*dJ^iO$DBD;u9_IGS$hiUus]US
Xne2DG@Jc@2mP%UXB`OU"NVclqIMhg3UZI-q#oi99MDL"%=Jn=6D9ki1`/!Y>)*m4AOEC<-SBqM,#@/@T_a]ka7k>k2f8#)<[4lOgU8dXe4YF8,PeDHd
^2\5eAg(%qQ!.a0VbDG[_[q5<F_t62qCcUX=s8lU']bVO8$d#GWBdGMbp85B'L3On,8(l^g?V^378\3eC_tnFJ48-48_lJ$qs:\n^RW#s,\+F+MM"75,
p%VT!S)IO@N8>uoWtL(p5e7EEP2=Y'1%2Fg3(97n]O.'9fY3.]Btl`Q)2P?jqBcC;+=n465;J0C>G]5d5*`@ojUTuMa:^+;(^';f<I-=&);7YK"]Qh>u
ndqtEf3I.pagjfq=n@Yp#([4CM&SCmiSe!1W@;0mXr9onp"PN<[j,)G^7l85)A]*X[NC^qdGJ2IiGF53W?K,5R]Glmfl\',D&WBNC$%[!9Y)VkSKq>bO
D`7*@)>d<jd[9Uh,Z&p,#3=)7LPBe*(4p;FWnd/>c%FPBp=c>\meH/e:EVr;,=>@('<lt1;#<f%r*7TedR\?q/JdTM"a0'u^^F[QajNRfG,/.e189<4=
D^9<0f!,bhnI.G->c</jK-k\3Ltd/?]Ff0?LZ1]3U3]jLRL$5??G)`3[GeQ"RZ6XI$/(p_R0\t&64[d6,dM(*_7Q9.HpjqbmZ/dgo(HKJGhBTle.N)IN
hiaTEDa$8gLoa#bPE9qQ,Xt!.H8^O5CB70_Xs`Z:trDs"D9F>8&bXpBcoNqX9H2C&QU5V$84p32?fkcC1`nbYKHYe`m'*^q\c\l1YcGq*C-Ujfrrti:#
^RQqiW,-8%O4cpjqJ`fA>C0,'V6JC9U`#a;Z#]re"'7pfs!,-%AM[X(LDlq(n_J%pA;Rqd-rl^`jh#5H3?n+lL-:g.@D$%[!Ag:V1c@"-]oLNQTIgm/i
^^e!5,_Ib=LR@_Q=Lm:O'3'D>DmifOXJ'q\+OSD.H[#kMVjO:bC!JboUoq98A3hp,e&]CZ*qg9DUD,1VY#Kj#DQ3G/nQ--N=Xe:RNmA?=4`!$\;gXhg6
;!$:3@iRH''Jf'Vqb?^e94&(qbb)BTp65k5r6Sm3Gl>E1R.g!r4OaqHH([c.Qm5:+>7RoHXFnp%C23[8=Ja18f(ZH7\re<bW-h_Me9%A!N[9.diR$iZI
Nl_ljI?rO]gtK2E';6*(Ojtih67kA937_<UA9l-^R_D7]&VircFdU>Q\F?g-kia\(LS>uK+STaZO^MlBjJ9uFkr86[F@k!^CIKP[#0Z3.=`9DAO'AK70
d\o=S<"qi&MSB\aIoJ)[VI+gX>j<_E&IGf>M"*rR"7'=&q+)]&B//Ad++fSb)R.<TqA@'#3=EQ93g@!HuObmke**M94E=@b&VN5eZltEeZSC<1lV_aYI
%BqT?l[h!]$I0QSfk+fqQ,&b:<_3I_Q4alF@oN5;d2AFojJQ;<X%iiC%bnqEP8<ae[U^#M=&"P&4@fS%As<&C+tj%S[]<b2"6=A1id!."VF1)-K2HNpa
)!!/uMU4iUJ8mOKNZ,C;P!WW3#!!HG.'''
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

version = '1.37'
VERSION = version
__version__ = version
COMMIT_DATE = '2025-12-16'

SMARTCTL_PATH = shutil.which("smartctl")

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
		device_name, _, line = line.partition(' on ')
		if device_name.startswith(os.path.sep):
			device_name = os.path.realpath(device_name)
		mount_point, _, line = line.partition(' type ')
		fstype, _ , options = line.partition(' (')
		options = options.rstrip(')').split(',')
		mount_table[device_name].append(MountEntry(mount_point, fstype, options))
	return mount_table

def get_blocks():
	# get entries in /sys/class/block
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
	if not sysfs_block_path or not os.path.isdir(sysfs_block_path):
		return 512
	if get_partition_parent_name(sysfs_block_path):
		sysfs_block_path = os.path.join('/sys/class/block', os.path.basename(get_partition_parent_name(sysfs_block_path)))
	sector_size = read_int(os.path.join(sysfs_block_path, "queue", "hw_sector_size"))
	if sector_size == 0:
		sector_size = read_int(os.path.join(sysfs_block_path, "queue", "logical_block_size"))
	return sector_size if sector_size else 512

def get_read_write_rate_throughput_iter(sysfs_block_path):
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
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
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
	if {'SIZE','FSTYPE','UUID','LABEL'}.intersection(output_fields_set):
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
			parent_sysfs_path = os.path.realpath(os.path.join('/sys/class/block', os.path.basename(parent_name))) if parent_name else None
			if 'MODEL' in output_fields_set or 'SERIAL' in output_fields_set:
				device_properties['MODEL'], device_properties['SERIAL'] = read_model_and_serial(parent_sysfs_path)
			if 'DISCARD' in output_fields_set:
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