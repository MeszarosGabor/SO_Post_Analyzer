* ctaf1402.txt
   - tree

* mcfpat1402-with_issue_date.txt
    File Characteristics
        Record Length
            26 Characters - 18 characters (from original mcfpat1402.txt) + 8 characters (issue date from USPTO web pages)

        U.S. Patent Number - A 7-position alphanumeric field.

            Utility Patent
                7 numeric positions right justified with leading zeros.

            Design Patent
                "D" followed by 6 numeric positions right justified with leading zeros.

            Statutory Invention Registration (SIR)
                SIR Utility
                    "H" followed by 6 numeric positions right justified with leading zeros.
                SIR Design
                    "HD" followed by 5 numeric positions right justified with leading zeros.
                SIR Plant
                    "HP" followed by 5 numeric positions right justified with leading zeros.

            Plant Patent
                "PP" followed by 5 numeric positions right justified with leading zeros.

            Reissue Patent
                Reissue Utility
                    "RE" followed by 5 numeric positions right justified with leading zeros.
                Reissue Design
                    "RD" followed by 5 numeric positions right justified with leading zeros.
                Defensive Publications
                    "T" followed by 6 numeric positions right justified with leading zeros.
                "X" Patent
                    "X" followed by 6 numeric positions right justified with leading zeros.
                "X" Reissue Patent
                    "RX" followed by 5 numeric positions right justified with leading zeros.
                Additional Improvements
                    "AI" followed by 5 numeric positions right justified with leading zeros.

        U.S. Patent Classification – A 9-position alphanumeric field.
            Classification – A 3-position alphanumeric field right justified with leading zeros.
            Subclassification – A 6-position alphanumeric field right justified with leading zeros.

        U.S. Patent Classification Type Code – A 1-position alphabetic field.
            "O" for Original Classification
            "X" for Cross Reference Classification
        
        Issue Date - A 8-position numeric field. equivalent to 'Grant year'
            YYYYMMDD
                YYYY : year
                MM   : month
                DD   : day

            **NOTICE**
                If a patent was withdrawn, a web page of the patent does not have issue date information. 
                In this case, we considered its issue date as 00000000.
                
                patent_list_date_str_00000000.txt contains withdrawn patent list.
                

        Linefeed - A 1-position alphanumeric field that contains: Hexidecimal "OA"

        Reference
            http://storage.googleapis.com/patents/patent_classification_information/USPatentGrantMasterClassDocumentation.doc


    How to make it?
        mcfpat.zip is accessible online at http://www.google.com/googlebooks/uspto-patents-class.html
            This zip file we obtained (April 8 2014) contains mcfpat1402.txt
            This file contains patent type, number, classification, subclassification, whether it is primary
            This file does not include issue date information for each patent.
        
        USPTO Patent Full-Text Database Number Search is accessible online at http://patft.uspto.gov/netahtml/PTO/srchnum.htm
        
        First, we made a set of patents from mcfpat.zip
        
        Second, we sent a query for a patent to USPTO patent full-text database
            number search, got a web page for the patent, and saved the page as a html file. 
            We iteratively obtained the files for 9,405,664 patents. 
            This process was performed from April 21 2014 to April 28 2014).
            To get a web page, we used "requests" which is a python library 
            and implemented our code as a multithread one for speedy crawling.
                http://docs.python-requests.org/en/latest/
            Patent type U and D were classified in 30,000 files because huge number of files have these types 
        
        Next, we extracted issue date information from the files.
            The web pages provide month information as a word format rather than two digit integers in both issue date and filed date.

            Here we extracted issue date information because web pages for patents before 1971 do not have filed date information.
                For example please check a difference between two pages: 
                    http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&d=PALL&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&r=1&f=G&l=50&s1=3552243.PN.&OS=PN/3552243&RS=PN/3552243
                    http://patft.uspto.gov/netacgi/nph-Parser?Sect1=PTO1&Sect2=HITOFF&d=PALL&p=1&u=%2Fnetahtml%2FPTO%2Fsrchnum.htm&r=1&f=G&l=50&s1=3552244.PN.&OS=PN/3552244&RS=PN/3552244

            
            Issue date parsing detail
                As we mentioned before, web pages of a patent are classified by existence of filed date or abstract
                Therefore we should carefully parse the web pages

                If a web page does not have abstract or filed date, issue date information appears next to the following string
                    Type 1 (up to U3552243 ~ 1971)
                        <TD VALIGN=TOP ALIGN="RIGHT" WIDTH="80%"><B>

                If the web page does not include abstract or filed date, issue
        date information appears next line of the following string
                    Type 2 (from U3552244 ~ 1971)
                        after
                            <TD ALIGN="RIGHT" WIDTH="50%"> <B>
            


        Finally, we combined a patent list in mcfpat1402.txt and issue date information obtained from USPTO webpage files and constructed
 "mcfpat1402-with_issue_date.txt".


* mcfpat1402-with_filed_date.txt
    File Characteristics
        Record Length
            26 Characters - 18 characters (from original mcfpat1402.txt) + 8 characters (filed date from USPTO web pages)
    
    This file contains technology classification and subclassification codes of 9405664 patents. 
    Filed date information of 5506795 patents has been tagged.
    14 patents do not have day information among 5506795 patents.
        19691200, 19820900, 19811100, 19910200, 19861000, 
        19770300, 19700300, 19850300, 19851000, 19680500, 
        19831100, 19840600, 19691100, 19850200
        

    The rest of this file is same as mcfpat1402-with_issue_date.txt


* patent_list_date_str_00000000.txt
    This file includes withdrawn patents which do not have issue date information.

* patent_list_inaccessible.txt
    This text file contains patents whose webpages do not exist.


* pat2invt_info_2011-2014.txt
    data from USPTO webpage (parsed). 


