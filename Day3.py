# Task 1
import psycopg2

conn = psycopg2.connect(
    dbname='Db1',
    user="postgres",
    password='7887',
    host="localhost",
    port=5432
)

cur = conn.cursor()

def create_company(company_name , email):
    cur.execute(
        """
insert into companies (company_name, email)
values(%s, %s) returning CR_number
""", (company_name, email)
    )
    new_company_id = cur.fetchone()[0]
    conn.commit()
    return new_company_id

def get_company(cr_number):
    cur.execute('select * from companies where CR_number = %s', (cr_number,))
    company = cur.fetchone()
    return company

def update_company(cr_number, new_name, new_email):
    cur.execute(
        '''
update companies
set company_name = %s, email = %s
where CR_number = %s
''', (new_name, new_email, cr_number)
    )
    conn.commit()
    return cur.rowcount

def delete_company(cr_number):
    cur.execute('Delete from companies where cr_number = %s',(cr_number,))
    conn.commit()
    return cur.rowcount
    

# new_company_id = create_company('xyz', 'info@xyz.com')
# print(f'New company added with CR_number : {new_company_id}')

# company_details = get_company(6)
# print(f'company details: {company_details}')

# row_updated = update_company(6, 'Technistani', 'info@technistani.com')
# print(f'rows updated : {row_updated}')

row_deleted = delete_company(6)
print(f'row deleted : {row_deleted}')

cur.close()
conn.close()


# Task 2
