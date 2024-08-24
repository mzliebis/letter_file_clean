import pandas as pd
from pathlib import Path
import os
import glob
import sys


if __name__ == '__main__':

    # path set up
    path_project = Path.cwd().parent
    path_data = Path(path_project / "data")
    path_out = Path(path_project / "out")

    # delete files in out directory
    files = glob.glob('../out/*')
    print(files)
    for f in files:
        os.remove(f)

    # file import
    file_name = "af_recent_gifts_08_16_2024.CSV"


    df = pd.read_csv(path_data / file_name,  encoding='latin1')

    df = df.rename(columns={"Gf_Date": "Gift_Date",
                            "Gf_CnBio_ID": "Constituent_ID",
                            "Gf_Amount": "Gift_Amount",
                            "Gf_Type": "Gift_Type",
                            "Gf_Fund": "Fund_Code",
                            "Gf_Fnds_1_01_Description": "Fund_Description",
                            "Gf_CnBio_Last_Name": "Last_Name",
                            "Gf_CnBio_Constit_Code": "Constituent_Code",
                            "Gf_Acknowledge": "Gift_Acknowledged",
                            "Gf_CnAdrPrf_Addrline1": "Address_Line_1",
                            "Gf_CnAdrPrf_Addrline2": "Address_Line_2",
                            "Gf_CnAdrPrf_Addrline3": "Address_Line_3",
                            "Gf_CnAdrPrf_City": "City",
                            "Gf_CnAdrPrf_State": "State",
                            "Gf_CnAdrPrf_ZIP": "Zip_Code",
                            "Gf_CnAdrSalAll_1_01_Salutation": "Salutation_1",
                            "Gf_CnAdrSalAll_1_02_Salutation": "Salutation_2",
                            "Gf_CnAdrSalAll_1_01_Sal_Type": "Salutation_Type_1",
                            "Gf_CnAdrSalAll_1_02_Sal_Type": "Salutation_Type_2",
                            "Gf_Tr_1_01_Tribute": "Tribute_Type_1",
                            "Gf_Tr_1_01_Tribute_Description": "Tribute_1",
                            "Gf_Tr_1_02_Tribute": "Tribute_Type_2",
                            "Gf_Tr_1_02_Tribute_Description": "Tribute_2",
                            "Gf_CnBio_Org_Name": "Organization_Name",
                            "Gf_Import_ID": "Gift_Import_ID",
                            "Gf_AttrCat_1_01_Description": "IRA_Distribution",
                            "Gf_AttrCat_2_01_Description": "DAF/Trust"

                           })

    # remove gifts
    mask_1 = df['Constituent_Code'] == "Matching Gift Company"
    mask_2 = df['Constituent_Code'] == "Business"
    mask_3 = df['Constituent_Code'] == "Trust"
    mask_4 = df['Constituent_Code'] == "Foundation"
    mask_5 = df['IRA_Distribution'] == "Yes"
    mask_6 = df['DAF/Trust'].notna()



    mask = mask_1 | mask_2 | mask_3 | mask_4 | mask_5 | mask_6

    df = df[~mask]








    # extract Gomez addressee and salutation
    mask_addressee = df['Salutation_Type_1'] == "Gomez Addressee"
    df.loc[mask_addressee, 'Addressee'] = df['Salutation_1']

    mask_addressee = df['Salutation_Type_2'] == "Gomez Addressee"
    df.loc[mask_addressee, 'Addressee'] = df['Salutation_2']

    mask_addressee = df['Salutation_Type_1'] == "Gomez Salutation"
    df.loc[mask_addressee, 'Salutation'] = df['Salutation_1']

    mask_addressee = df['Salutation_Type_2'] == "Gomez Salutation"
    df.loc[mask_addressee, 'Salutation'] = df['Salutation_2']

    # business addressee adjustment
    mask = df['Addressee'].isna()
    mask = mask & (df['Constituent_Code'] == "Business")
    df.loc[mask, 'Addressee'] = df['Organization_Name']



    # clean up
    df = df[[ "Gift_Import_ID", 'Gift_Date', 'Gift_Type',
              'Constituent_ID', 'Last_Name', 'Constituent_Code',
             'Salutation', 'Addressee', 'Gift_Acknowledged',
             'Gift_Amount', 'Fund_Code', 'Fund_Description',
             'Tribute_Type_1', 'Tribute_1',
             'Tribute_Type_2', 'Tribute_2', 'Address_Line_1',
             'Address_Line_2',  'Address_Line_3', 'City',
             'State', 'Zip_Code']]

    # clean up fund descriptions
    df['Fund_Description'] = df['Fund_Description'].str.replace("03-410026-13-2408", "The Wrestling Program")
    df['Fund_Description'] = df['Fund_Description'].str.replace("RES-Specific Restricted Tuition", "Tuition Support")
    df['Fund_Description'] = df['Fund_Description'].str.replace("Restricted Gifts", "The Restricted Gifts Fund")

    #df['Constituent_ID'] = df['Constituent_ID'].astype(int)

    df['Address_Line_Total'] = df['Address_Line_1']
    mask = df['Address_Line_2'].notna()

    df.loc[mask, 'Address_Line_Total'] = df['Address_Line_Total'] + ", " + df['Address_Line_2']

    # remove missing address
    mask = df['Address_Line_1'].isna()
    df = df[~mask]

    # remove estate gifts
    mask = df['Constituent_Code'] != "Estate"
    df = df[mask]

    # remove gift of dollar value zero
    mask = df['Gift_Amount'] != "$0.00"
    df = df[mask]

    # remove anonymous gifts
    mask = df['Last_Name'] != "Anonymous"
    df = df[mask]

    # gifts that are not acknowledged
    mask = df['Gift_Acknowledged'] != "Acknowledged"
    df = df[mask]

    # remove MGC
    mask = df['Constituent_Code'] != "Matching Gift Company"
    df = df[mask]

    # for businesses if no saluatation add Friend
    mask = df['Salutation'].isna()
    mask = mask & (df['Constituent_Code'] == "Business")
    df.loc[mask, 'Salutation'] = "Friend"


    # zip code fix
    df['Zip_Code'] = df['Zip_Code'].astype(str).str.zfill(5)

    # salutation is missing
    mask = df['Salutation'].isna()
    error_toggle = False
    if mask.sum() > 0:
        error_toggle = True
        print("\n************************** Salutation Missing  ************************************************\n")

        print(df.loc[mask,['Constituent_ID', 'Salutation']].to_markdown())

    # salutation ends in and
    mask = df['Salutation'].str.endswith(" and")
    error_toggle = False
    if mask.sum() > 0:
        error_toggle = True
        print("\n************************** Salutation ends with and  ************************************************\n")

        print(df.loc[mask, ['Constituent_ID', 'Salutation']].to_markdown())



    # lower case salutation
    mask = df['Salutation'].str[0].str.islower()
    if mask.sum() > 0:
        error_toggle = False
        print("\n************************* Lower Case Salutation Issue ******************************************\n")
        print(df.loc[mask, ['Constituent_ID', 'Salutation']].to_markdown())

    # catch addressee and salutation have mismatch of number of people
    mask_1 = df['Salutation'].str.contains(" and ")
    mask_2 = df['Addressee'].str.contains(" and ")
    mask_3 = df['Addressee'].str.contains(" & ")
    mask_4 = mask_2 | mask_3
    mask_3 = (mask_1 != mask_4)
    if mask_3.sum() > 0:
        print("\n****************************  Addressee and Salutation Mismatch  **************************")
        print(df.loc[mask_3, ['Constituent_ID', 'Salutation', 'Addressee']].to_markdown())

    # Potential city address issues
    temp = df['City'].str.title()
    mask = (temp != df['City'])
    if mask.sum() > 0:

        print("**********************************************************************************")
        print("city address issue")
        print(df.loc[mask, ['Constituent_ID', 'City']].to_markdown())

    # tribute issue
    mask =(df['Tribute_Type_1'].notna()) & (df['Tribute_1'].isna())
    if mask.sum() > 0:

        print("**********************************************************************************")
        print("tribute 1 issue")
        print(df.loc[mask, ['Constituent_ID', 'Gift_Amount','Tribute_Type_1', 'Tribute_1']].to_markdown())

    # tribute issue
    mask = (df['Tribute_Type_2'].notna()) & (df['Tribute_2'].isna())
    if mask.sum() > 0:
        print("**********************************************************************************")
        print("tribute 2 issue")
        print(df.loc[mask, ['Constituent_ID', 'Tribute_Type_2', 'Tribute_2']].to_markdown())



    if error_toggle:
        sys.exit("problem with data")

    # sort
    df = df.sort_values(by=['Last_Name'], ascending=True)

    # split file into stock gifts and non stock gifts
    stock_gift_id = ["Stock/Property (Sold)", "Stock/Property"]
    mask = df['Gift_Type'].isin(stock_gift_id)
    df_stock = df[mask]
    df = df[~mask]

    # split file into recurring gift
    recurring_gift_id = ["Recurring Gift Pay-Cash"]
    mask = df['Gift_Type'].isin(recurring_gift_id)
    df_recurring = df[mask]
    df = df[~mask]

    # multiple gifts from same constituent
    count = df['Constituent_ID'].value_counts()
    count = count[count>1]
    duplicates = count.keys().astype(int)

    mask = df['Constituent_ID'].isin(duplicates)
    df_duplicates = df[mask]
    df = df[~mask]

    df.to_excel(path_out / "output.xlsx", index=False)
    df_stock.to_excel(path_out / "output_stock.xlsx", index=False)
    df_recurring.to_excel(path_out / "output_recurring.xlsx", index=False)
    df_duplicates.to_excel(path_out / "output_duplicates.xlsx", index=False)





