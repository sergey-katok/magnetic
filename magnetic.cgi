#!C:\Perl\bin\Perl.exe

MAIN:
{

#axes of circle loops are parallel

print "Content-type: text/html\n\n";

use CGI::Carp qw(fatalsToBrowser);

use Math::Cephes qw(:elliptics :trigs);
$pi = 3.14159265358979;
$convert = $pi/180;

$color = qw(white yellow orange pink green); #colors for loop "centers"

#ellpe:  Complete elliptic integral of the second kind
#ellpk:  Complete elliptic integral of the first kind


############# PARAMETERS ################
#image params#####
$D = 2500; #shift of z-axe
$ww=3500; $hh=1600;# px width and height of lower half graph
$hh1 = $hh+$D;

#iteration params#######
$N = 12; #number of lines 1st set, def=12
$l = 3; #px length of one interval, def=3
$steps = 100; #steps for each line def=500

$a=200; #scale size in px, def=200

#loops params#####

@aa = (1,  1,   -1);#currents inside of each loop
@RR = (0.3,0.3,0.3);#radius of each loop
@XX = (3,  3,    3);#r-coordinates of centers of each loop
@ZZ = (0, -0.5, -1); #z-coords; height between two loops def=3
@ff = (0,  0,    0);#angle to x-axis
#$aa[1] = 1;   $aa[2] = 1;    $aa[3] = -1;
#$RR[1] = 0.3; $RR[2] = 0.3;  $RR[3] = 0.3;
#$ff[1] = 0;   $ff[2] = 0;    $ff[3] = 0;
#$ZZ[1] = 0;   $ZZ[2] = -0.5; $ZZ[3] = -1;
#$XX[1] = 3;   $XX[2] = 3;  $XX[3] = 3;

$N_L = $#aa; #number of loops

#aux. params####
$show_axes = 0; #1=axes are shown

##############  IMAGE  ######################
use Image::Magick;
$file = '../htdocs/images/magnet1.jpg';
$image = Image::Magick->new;
$image->Set(size=>$ww.'x'.$hh1);
$image->ReadImage('xc:white');

#axes
$H = 0.5*$a;
$D1 = ($D-$H);
if($show_axes){
   $image->Draw(stroke=>'green', primitive=>'line', points=>"0,$D $ww,$D"); #x-axis1
   $image->Draw(stroke=>'blue', primitive=>'line', points=>"0,0 0,$hh1"); #y-axis
   $image->Draw(stroke=>'green', primitive=>'line', points=>"0,$D1 $ww,$D1"); #x-axis2
}

#current projections
$dsm = 2; #diameter of small circle in px.

#Loops loop
for($i=0;$i<=$N_L;$i++){

   $XX_R[$i] = ($XX[$i]+$RR[$i]*cos($ff[$i]));   $XX_R0[$i] = $XX_R[$i]*$a;
   $XX_RR[$i] = $XX_R0[$i]+$dsm;
   $XX_L[$i] = ($XX[$i]-$RR[$i]*cos($ff[$i]));   $XX_L0[$i] = $XX_L[$i]*$a;
   $XX_LL[$i] = $XX_L0[$i]+$dsm;

   $ZZ_R[$i] = ($ZZ[$i]+$RR[$i]*sin($ff[$i]));   $ZZ_R0[$i] = $ZZ_R[$i]*$a+$D;
   $ZZ_RR[$i] = $ZZ_R0[$i]+$dsm;
   $ZZ_L[$i] = ($ZZ[$i]-$RR[$i]*sin($ff[$i]));   $ZZ_L0[$i] = $ZZ_L[$i]*$a+$D;
   $ZZ_LL[$i] = $ZZ_L0[$i]+$dsm;

   $image->Draw(stroke=>$color[$i], primitive=>'circle', points=>"$XX_R0[$i],$ZZ_R0[$i] $XX_RR[$i],$ZZ_RR[$i]", fill=>$color[$i]); #ist loop right
   $image->Draw(stroke=>$color[$i], primitive=>'circle', points=>"$XX_L0[$i],$ZZ_L0[$i] $XX_LL[$i],$ZZ_LL[$i]", fill=>$color[$i]); #ist loop left

   &set($XX_L[$i],$ZZ_L[$i],$RR[$i],$ff[$i]);

}#end of loops loop

$image->Write($file);

print "<img src=/images/magnet1.jpg>";

print "<hr>END";
}
########################################################################
#set of lines
sub set{
local($X_L,$Z_L,$R_this,$f) = @_;

   for($n=1;$n<=($N-1);$n++){
      $x10 = $X_L*$a+$n*2*$R_this*$a*cos($f)/$N;
      $z10 = $Z_L*$a+$n*2*$R_this*$a*sin($f)/$N;
      $x20 = $x10;
      $z20 = $z10;
      &line; #1-upper,-1-low
   }
}

#########################################################################
sub line{
#one line loop
local($j);

 for($j=1;$j<=$steps;$j++){

   $teta1 = &teta($x10,$z10);
   if(!$teta1){last}
   $x1 = $x10 - $l*cos($teta1);
   $z1 = $z10 - $l*sin($teta1);

   $teta2 = &teta($x20,$z20);
   if(!$teta2){last}
   $x2 = $x20 + $l*cos($teta2);
   $z2 = $z20 + $l*sin($teta2);

   &draw_line($x10,$z10,$x1,$z1,'red');
   &draw_line($x20,$z20,$x2,$z2,'blue');

   $x10 = $x1;
   $z10 = $z1;

   $x20 = $x2;
   $z20 = $z2;

 }#end of one line loop

}

##################################################################################

sub teta{

local($x,$z) = @_;
local($b_rr,$b_zz,$j);
local($b_z,$b_r) = (0,0);

#Loops loop
for($j=0;$j<=$N_L;$j++){
   local($b_rr,$b_zz) = &B($x,$z,$XX[$j]*$a,$ZZ[$j]*$a,$RR[$j]*$a);
   $b_r = $b_r+($aa[$j]*$b_rr);
   $b_z = $b_z+($aa[$j]*$b_zz)
 }#end of loops loop

if($b_z eq 0 and $b_r eq 0){return}
local($teta) = atan2($b_z,$b_r);
return $teta;

}

###########################################

sub B{
local($rr,$z,$R,$Z,$A) = @_;
local($r) = abs($rr-$R);
if($r eq 0){return 0,1}

local($k) = sqrt((4*$A*$r)/(($A+$r)**2+($z-$Z)**2));
if((($A-$r)**2+($z-$Z)**2) eq 0){print "r=$r;z=$z;Z=$Z"; return}
local($Q1) = &E($k)*($A**2-$r**2-($z-$Z)**2)/(($A-$r)**2+($z-$Z)**2);
local($Q2) = &E($k)*($A**2+$r**2+($z-$Z)**2)/(($A-$r)**2+($z-$Z)**2);

local($b_r) = (-&K($k)+$Q2)*$k*($z-$Z)/($r*sqrt($r));
local($b_z) = (&K($k)+$Q1)*$k/sqrt($r);

if($rr<$R){$b_r = -$b_r}

return $b_r,$b_z;
}
###########################################################################

sub draw_line{
#shifted line
local($x0,$y0,$x1,$y1,$color) = @_;
$y0 += $D; $y1 += $D;
$image->Draw(stroke=>$color,primitive=>'line', points=>"$x0,$y0 $x1,$y1");
}

###################################################################

#elliptic integrals
sub E{
local($k)=@_;

return ellpe(1-$k**2);
}

sub K{
local($k)=@_;
return ellpk(1-$k**2);
}

############################################################################

#convert degrees to radians
sub deg2rad{
local($deg) = @_;
return $deg*$convert;
}
