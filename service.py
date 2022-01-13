from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode, AnyDict, AnyXml
from spyne.model.complex import ComplexModel
from lxml import etree
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
import cx_Oracle
import base64

class SoapService(ServiceBase):
    @rpc(Unicode,
            _returns=[Iterable(AnyDict),Iterable(AnyDict),Iterable(AnyDict),Iterable(AnyDict),Iterableterable(AnyDict),Iterable(AnyDict)]
            _out_variable_names=["hd_persons","hd_attestat","hd_awards","hd_education","hd_work", "hd_photo"],
            _out_message_name="Response",
            _operation_name="soap")
    def soap(ctx,iin):

        #selects
        sql = ["select g.*, n.name nation_name, s.name sex_name, p.name position_name from hd.g_persons g left join hd.s_nations n on g.nation_id = n.id left join hd.s_sex s on g.sex = s.id left join hd.s_positions p on g.position_id = p.id where g.iin = :iinumber",
        "select a.*, aa.name arrivalsource_name, ar.name arrivalreason_name from hd.hd_arrival a left join s_arrivalsource aa on a.arrivalsource_id = aa.id left join hd.s_arrivalreasons ar on a.reason = ar.id where person_id in (select id from hd.g_persons where iin = :iinumber)",
        "select a.*, asol.name attestatsolution_name from hd.hd_attestat a left join hd.s_attestatsolutions asol on a.attestatsolution_id = asol.id  where prs_id in (select id from hd.g_persons where iin = :iinumber)",
        "select * from hd.hd_awards where person_id in (select id from hd.g_persons where iin = :iinumber)",
        "select max(id) as photo_id from hd.hd_photos where person_id in (select id from hd.g_persons where iin = :iinumber)"]
        
        #empty xml
        result = []

        dsn = cx_Oracle.makedsn("192.168.66.230", 1521, service_name="wls")
        conn = cx_Oracle.connect("sel", "password", dsn)
        
        #select photo
        query = "select photo from (select * from hd.hd_photos where person_id in (select id from hd.g_persons where iin = :iinumber) order by id desc)  where rownum =1"
        cur2 = conn.cursor()
        cur2.execute(query,{"iinumber":iin})
        obj = cur2.fetchone()
        imageBlob = obj[0]
        image_64_encode = base64.encodebytes(imageBlob.read())
        photo = {'photo':str(image_64_encode)}
        
        
        for select in (sql):       
            
            columns = []   #column list
            table = []     #table (list of row)
            cur = conn.cursor()
            cur.execute(select,{"iinumber":iin})
            
            for y in range(0, len(cur.description)):
                #print(cur.description[y])
                columns.append(cur.description[y][0]) #make columns names list
            
            res = cur.fetchall()
            for row in res: #for all rows in table
                row = dict(zip(columns, row)) #make pair col_name:value (node xml)
                table.append(row)   #append row to table
            
            result.append(table)
        
        #Adding dict (with image) to last element
        result[-1].append({"PHOTO":str(image_64_encode)})
        conn.close()
        return result

def on_methohd_return_string(ctx):
        ctx.out_string[0] = ctx.out_string[0].replace(b'tns:anyType>', b'row>')


SoapService.event_manager.adhd_listener('methohd_return_string', on_methohd_return_string)

application = Application([SoapService], 'spyne.soap',
                          in_protocol=Soap11(validator='lxml'),
                          out_protocol=Soap11(polymorphic=True))

wsgi_application = WsgiApplication(application)


if __name__ == '__main__':
    import logging

    from wsgiref.simple_server import make_server

    #logging.basicConfig(level=logging.DEBUG)
    #logging.getLogger('spyne.protocol.xml').setLevel(logging.DEBUG)

    logging.info("listening to http://127.0.0.1:6767")
    logging.info("wsdl is at: http://localhost:6767/?wsdl")

    server = make_server('192.168.66.98', 6767, wsgi_application)
    server.serve_forever()
