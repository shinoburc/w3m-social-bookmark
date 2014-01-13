#!/usr/bin/perl

use LWP::Simple;
use CGI;
my $use_nkf = eval 'use NKF;1';

my $form = new CGI;

my $end_of_section = "<!--End of section (do not delete this comment)-->";
my $encoding = "-e";

my $form_category      = "category";
my $form_new_category  = "new_category";
my $form_uri           = "uri";
my $form_title         = "title";
my $form_doPost        = "doPost";

my $bookmark_file = "bookmark.html";

print << "HTML_HEAD";
Content-type: text/html

<html>
    <head>
        <META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=EUC-JP">
        <title>MY BOOKMARK</title>
    </head>
    <body>
        <h1>MY BOOKMARK</h1>
        <form name="main" method="POST">
HTML_HEAD

if($form->param($form_doPost) eq "do"){
    &add_bookmark($form->param($form_title),$form->param($form_uri),$form->param($form_new_category),$form->param($form_category));
} elsif (defined $ENV{'HTTP_REFERER'}){
    my $bookmark_content = &parse($bookmark_file);

    if($use_nkf){
        &output_title_text_box(nkf($encoding,&get_title($ENV{'HTTP_REFERER'})));
    } else {
        &output_title_text_box(&get_title($ENV{'HTTP_REFERER'}));
    }
    &output_uri_text_box($ENV{'HTTP_REFERER'});
    &output_new_category_text_box();
    &output_category_select_box($bookmark_content);
}

print << "HTML_FOOT";
        <p>
        <input type="hidden" name="doPost" value="do">
        <input type="submit">
        </form>
    </body>
</html>
HTML_FOOT

sub add_bookmark($$$$){
    my ($title,$uri,$new_category,$category) = @_;

    open(BK,"<" . $bookmark_file) or die "Cannot open $bookmark_file : $!\n";
    my @lines = <BK>;
    close(BK);

    open(BK,">" . $bookmark_file) or die "Cannot open $bookmark_file : $!\n";
    if($new_category eq ""){
        while(my $line = shift @lines){
            print BK $line;
            if($line =~ /<h2>(.*)<\/h2>/){
                if($category eq $1){
                    print BK shift @lines;
                    print BK '<li><a href="' . $uri . '">' . $title . '</a>' . "\n";
                }
            }
        }
    } else {
        while(my $line = shift @lines){
            if($line =~ /<\/body>/){
                print BK "<h2>" . $new_category . "</h2>\n";
                print BK "<ul>\n";
                print BK '<li><a href="' . $uri . '">' . $title . '</a>' . "\n";
                print BK $end_of_section . "\n";
                print BK "</ul>\n";
                print BK "</body>\n";
                print BK "</html>\n";
                last;
            }
            print BK $line;
        }
    }
    close(BK);

    print 'return : <li><a href="' . $uri . '">' . $title . '</a>' . "\n";
}

sub get_title{
    my $uri = shift;
    my $doc = get $uri;
    $doc =~ s/\x0D\x0A|\x0D|\x0A/ /g;
    if($doc =~ /<title>(.*)<\/title>/i){
        return $1;
    } else {
        return 'NO TITLE';
    }
}

sub parse($){
    my $bookmark_file = shift;

    my $category;
    my %rtn;
    
    open(IN,"<" . $bookmark_file) or die "Cannot open $bookmark_file : $!\n";

    while(<IN>){
        if(/<h2>(.*)<\/h2>/){
           $category = $1; 
        }
        if(/<li><a href="(.*)">(.*)<\/a>/){
            $rtn{$category}{$1} = $2;
        }
    }
    close(IN);
    return \%rtn;
}

sub output_title_text_box($){
    my $title = shift;
    print '<br>' . $form_title . ' : <input type="text" name="' . $form_title . '" value="' . $title . '">';
}

sub output_category_select_box($){
    my $content = shift;
    %content = % { $content };

    print '<br>' . $form_category . ' : <select name="' . $form_category . '">' . "\n";
    foreach my $category (keys %content){
        print "<option value=\"$category\">" . $category . "</option>\n";
    }
    print "</select>\n";
}

sub output_new_category_text_box(){
    print '<br>' . $form_new_category . ' : <input type="text" name="' . $form_new_category . '">' . "\n";
}

sub output_uri_text_box($){
    my $uri = shift;
    print '<br>' . $form_uri . ' : <input type="text" name="' . $form_uri . '" value="' . $uri . '">';
}
