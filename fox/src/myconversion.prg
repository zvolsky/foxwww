* uncomment for debugging
*!*	DO MyConv WITH 'c:\codex_\codex\dbfs', FULLPATH('..\..\data\fox\')    && working dir == vfp project dir

* uncomment for final
LPARAMETERS lfSrcData
DO MyConv WITH m.lfSrcData, FULLPATH('') + 'data\fox\'     && working dir is from python proccess == python root project dir
QUIT



PROCEDURE MyConv(lfSrcData, lfCopyPath)
	lfSrcData = FULLPATH(ADDBS(m.lfSrcData))
* en, cz
*----------------------
* rest is just example (converts data from librarian software Codex)
* vse nize je je priklad - (prevadi data z knihovnickeho software Codex)
*-----------------------------------------------------------
* replace this with your own data conversion dbf->dbf

* this example joins more tables into one, but you can have more target tables
* single table will show itselves as a grid, more tables as grids with links

* target codepage must be supported by python module dbfread (most, but cz-Kamenicky, pl-Mazovia,..)
* newest vfp data types (Varchar, ..) aren't supported (by the python dbfread module, I think so at least)

* at the web (python/web2py) application level you have to describe the target data model once again
*     in modules/db_model.py, get_model() (but name there fields in lowercase)

* if you need relations (links to related records in web application) you should:
*    - add the field (id integer unique) to all tables (unique from AUTOINC or handle the unique value)
*         skip this id fields in the python model
*    - use integer foreign_keys, recommended name is <target-table>_id,
*         in python model use for foreign keys the type db.<target_table> or '<target_table>.id'

*----------------------
* toto nahrad vlastnim prevodem dat dbf->dbf

* zde priklad "sliti" do jedine tabulky, ale muze byt vice tabulek
* jedina tabulka bude zobrazena jako grid, vice relacne propojenych tabulek jako gridy s odkazy

* cilova codepage musi byt podporovana modulem dbfread (vetsina je, ale vyjimky: cz-Kamenicky, pl-Mazovia)
* nejnovejsi datove typy vfp (Varchar, ..) nejsou podporovany (python dbfread modulem, aspon se domnivam)

* cilovy datovy model je treba (duplicitne) popsat i ve webove python/web2py aplikaci
*     v modules/db_model.py, get_model() (ale tam pojmenujte vsechna pole lowercase (malymi pismeny))

* chcete-li relace (odkazy na zavisle zaznamy ve webove aplikaci) meli byste:
*    - pridat pole (id integer unique) do vsech tabulek (unique pomoci AUTOINC nebo unique hodnotu zajistete importem)
*         az budete definovat python model, id pole neuvadejte
*    - pouzit integer cizi klice, doporucene pojmenovani je <cilova-tabulka>_id
*         az budete definovat python model, pouzijte pro ne typ: db.<cilova_tabulka> nebo '<cilova_tabulka>.id'

	SET EXACT ON
	SET COLLATE TO 'machine'

	CREATE TABLE (m.lfCopyPath + 'Codex') FREE CODEPAGE=1250 ( ;
			ID Integer AUTOINC, ;
			Autori Memo, ;
			Osoby Memo, ;
			Nazev Character(254), ;
			Podnazev Memo, ;
			KlSl Memo, ;
			Dt Memo, ;
			Vydani Memo, ;
			Impresum Memo, ;
			Anotace Memo ;
			)

	cz = REPLICATE('1', 200)  && nutne pro otevreni pochybnych proprietarnich indexu (fake only -> NOUPDATE)
	USE (m.lfSrcData + 'Knihy') IN 0 SHARED AGAIN NOUPDATE ORDER Nazev
	USE (m.lfSrcData + 'K_Klsl') IN 0 SHARED AGAIN NOUPDATE ORDER ID_Publ
	USE (m.lfSrcData + 'Klsl') IN 0 SHARED AGAIN NOUPDATE ORDER ID
	USE (m.lfSrcData + 'K_Autori') IN 0 SHARED AGAIN NOUPDATE ORDER ID_Publ
	USE (m.lfSrcData + 'Autori') IN 0 SHARED AGAIN NOUPDATE ORDER ID
	USE (m.lfSrcData + 'K_Autori') IN 0 SHARED AGAIN NOUPDATE ALIAS K_Osoby ORDER ID_Publ
	USE (m.lfSrcData + 'Autori') IN 0 SHARED AGAIN NOUPDATE ALIAS Osoby ORDER ID
	USE (m.lfSrcData + 'K_Dt') IN 0 SHARED AGAIN NOUPDATE ORDER ID_Publ

	SELECT K_Klsl
	SET RELATION TO ID_KlSl INTO KlSl ADDITIVE
	SELECT K_Autori
	SET FILTER TO Vztah='A'
	SET RELATION TO ID_Autora INTO Autori ADDITIVE
	SELECT K_Osoby
	SET FILTER TO Vztah#'A'
	SET RELATION TO ID_Autora INTO Osoby ADDITIVE
	SELECT Knihy
	SET RELATION TO ;
				ID_Publ INTO K_Autori, ;
				ID_Publ INTO K_Osoby, ;
				ID_Publ INTO K_KlSl, ;
				ID_Publ INTO K_Dt ;
			 ADDITIVE

	SELECT Knihy
	SCAN
		INSERT INTO Codex ( ;
				Autori, Osoby, Nazev, Podnazev, KlSl, Dt, Vydani, Impresum, Anotace ;
			) VALUES ( ;
				Vice('Autori.Autor', 'K_Autori', ' - '), ;
				Vice('Osoby.Autor', 'K_Osoby', ' - '), ;
				Knihy.Nazev, ;
				Knihy.Podnazev, ;
				Vice('KlSl.KlSl', 'K_KlSl', ', '), ;
				Vice('K_Dt.Dt', 'K_Dt', ', '), ;
				Knihy.Vydani, ;
				Knihy.Impresum, ;
				Knihy.Anotace ;
				)
	ENDSCAN
ENDPROC

PROCEDURE Vice(tcVyraz, tcSkakatAlias, tcSpojka)
	LOCAL lcVice
		lcVice = ''

	SELECT (m.tcSkakatAlias)
	SCAN WHILE ID_Publ==Knihy.ID_Publ
		lcVice = IIF(EMPTY(m.lcVice), '', m.lcVice + m.tcSpojka) + ALLTRIM(EVALUATE(m.tcVyraz))
	ENDSCAN
	SELECT Knihy
	
	RETURN m.lcVice
ENDPROC

PROCEDURE ival(dummy)  && nutne pro otevreni pochybnych proprietarnich indexu (fake only -> NOUPDATE)
	RETURN 0
ENDPROC
PROCEDURE rodnecislo(dummy,dummy2)  && nutne pro otevreni pochybnych proprietarnich indexu (fake only -> NOUPDATE)
	RETURN ''
ENDPROC
