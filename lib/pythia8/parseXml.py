#!/usr/bin/python

from __future__ import print_function

substitutes = { "~u_L": "~u_1", "~u_R": "~u_2", "~c_L": "~u_3", "~c_R": "~u_4",
                "~d_L": "~d_1", "~d_R": "~d_2", "~s_L": "~d_3", "~s_R": "~d_4",
                "~b_L": "~d_5", "~b_R": "~d_6", "~e_L-": "~e_1", "~e_R-": "~e_2",
                "~mu_L-": "~e_3", "~mu_R-": "~e_4", "~b_1": "~d_5", "~b_2": "~d_6",
                "~t_1": "~u_5", "~t_2": "~u_6", "~tau_L-": "~e_5", "~tau_R-": "~e_6",
                "~tau_1-": "~e_5", "~tau_2-": "~e_6"
}

def create():
    f=open("/usr/share/pythia8-data/xmldoc/ParticleData.xml")
    g=open("pythia8particles.py","w")
    g.write ( "# created via smodels/lib/parseXml.py,")
    g.write ( " parsing pythia8's ParticleData.xml.\n" )
    g.write ( "\n" )
    g.write ( "particles={\n" )
    lines=f.readlines()
    f.close()
    pids = {}
    for line in lines:
            if not "<particle" in line: continue
            pos = line.find ( "spin" )
            line = line[:pos]
            deletes = [ '<particle id="', '"', '=', 'name', 'antiName' ]
            for d in deletes:
                line = line.replace ( d, "" )
            print ( line )
            tokens = line.split()
            # print ( tokens )
            pids[ tokens[1] ] = int( tokens[0] )
            if tokens[1] in substitutes.keys():
                pids[ substitutes [ tokens[1] ] ] = pids [ tokens[1] ]
            if len(tokens)>2:
                pids[ tokens[2] ] = - int ( tokens[0] )
                if tokens[1] in substitutes.keys():
                    pids[ substitutes [ tokens[1] ]+"bar" ] = pids [ tokens[2] ]

    for key, value in pids.items():
        g.write ( '  "%s":%d,\n' % ( key, value ) )
                
    g.write ( '  "gluino": 1000021\n' )
    g.write ( "}\n" )
    g.close()

if __name__ == "__main__":
    create()

