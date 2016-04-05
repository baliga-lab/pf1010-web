-- --------------------------------------------------------------------------------
-- procudure to fetch number of records for a given time range
-- --------------------------------------------------------------------------------
DELIMITER $$

CREATE procedure `get_measurement_count` (tab varchar(100), pdate date, OUT num int)
BEGIN
	set @GetSystem = concat('select count(*) from ',tab
			,' where time between ? and CURDATE() into @num');
	set @pdate = pdate;
	prepare stmt from @GetSystem;
	execute stmt using @pdate;
	set num = @num;
END;

$$


-- --------------------------------------------------------------------------------
-- Routine DDL
-- Note: procedure to update system status
-- --------------------------------------------------------------------------------
DELIMITER $$
CREATE PROCEDURE `update_system_status` ()
LANGUAGE sql
COMMENT 'this procedure will run everyday at 12am to see if any of the system tables need to 
be updated.
Conditions for update:
------------------------------
system status: pre-established
	if there is data in the measurements table for atleast 7 days in the range
	current_day - 14
	AND
	ammonium and nitrite < nitrate for the latest reading
Change status to established
---------------------------------
System status : established
	if No data is found in the range current_day - 7 days time range
Change status to suspended

	if ammonium and nitrite > nitrate for last 7 reading
Change status to pre-established
---------------------------------update_system_status
System status : suspended
	if any data is found for current_day -1
Change status to pre-established

	if no data is found for current_day - 90 days
	OR
	if events (remove_fish || remove_plants)
Change status to terminated'
BEGIN
	declare date_7_days date;
	declare date_14_days date;
	declare date_90_days date;
	declare date_1_days date;
	DECLARE done INT DEFAULT FALSE;
	declare sysid varchar(40);
	declare ammonium_num int;
	declare nitrite_num int;
	declare nitrate_num int;
	
	declare curr_state varchar(25);
	DECLARE sys_cursor CURSOR FOR select system_uid, state from systems;
	DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
	set num = 1;
	set date_7_days = (select DATE_SUB(CURDATE(), INTERVAL 7 DAY) as date from dual);
	set date_14_days = (select DATE_SUB(CURDATE(), INTERVAL 14 DAY) as date from dual);
	set date_90_days = (select DATE_SUB(CURDATE(), INTERVAL 90 DAY) as date from dual);
	set date_1_days = (select DATE_SUB(CURDATE(), INTERVAL 1 DAY) as date from dual);
	open sys_cursor;
	systems_loop: loop

		fetch sys_cursor into sysid, curr_state;

		IF done then
			LEAVE systems_loop;
		END IF;		

		/*logic for pre-established systems*/
		if curr_state = 'PRE-ESTABLISHED' then
			/*check ammonium values*/
			call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_14_days, ammonium_num);
			/*check nitrate values*/
			call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_14_days, nitrate_num);
			/*check nitrite values*/
			call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_14_days, nitrite_num);

			if ammonium_num >= 7 then
				select "change to Established";
			else
				select "no change";
			end if;
		end if;

		/*logic for established systems*/
		if curr_state = 'ESTABLISHED' then
			/*check ammonium values*/
			call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_7_days, ammonium_num);
			/*check nitrate values*/
			call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_7_days, nitrate_num);
			/*check nitrite values*/
			call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_7_days, nitrite_num);

			if ammonium_num < 7 then
				select "change to Suspended";
			else
				select "no change";
			end if;
		end if;

		/*logic for suspended systems*/
		if curr_state = 'SUSPENDED' then
			/*check ammonium values*/
			call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_90_days, ammonium_num);
			/*check nitrate values*/
			call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_90_days, nitrate_num);
			/*check nitrite values*/
			call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_90_days, nitrite_num);
			if ammonium_num = 0 then
				select "change to Terminated";
			else
				select "no change";
			end if;
		end if;

		
	end loop;
	close sys_cursor;
END;

$$

CREATE PROCEDURE `check_pre_established` (sysid varchar(40), OUT ret int)
BEGIN
	declare date_14_days date;
	declare ammonium_num int;
	declare nitrite_num int;
	declare nitrate_num int;
	set date_14_days = (select DATE_SUB(CURDATE(), INTERVAL 14 DAY) as date from dual);
	/*check ammonium values*/
	call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_14_days, ammonium_num);
	/*check nitrate values*/
	call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_14_days, nitrate_num);
	/*check nitrite values*/
	call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_14_days, nitrite_num);

	/*logic for checking if plants and fish are added needs to be added here*/
	/*can a system go to terminated status if thrs no data for 90 days???*/

	/*check if there are atleast 7 readings*/
	if ammonium_num >= 7 and nitrate_num >= 7 and nitrite_num >= 7 then
		/*change to established*/
		set ret = 1;
	else
		set ret = 0;
	end if;
END

$$

CREATE PROCEDURE `check_established` (sysid varchar(40), OUT ret int)
BEGIN
	declare date_7_days date;
	declare ammonium_num int;
	declare nitrite_num int;
	declare nitrate_num int;
	set date_7_days = (select DATE_SUB(CURDATE(), INTERVAL 7 DAY) as date from dual);
	/*check ammonium values*/
	call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_7_days, ammonium_num);
	/*check nitrate values*/
	call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_7_days, nitrate_num);
	/*check nitrite values*/
	call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_7_days, nitrite_num);
	if ammonium_num < 1 and nitrate_num < 1 and nitrite_num < 1 then
		select "change to suspended";
		set ret = 1;
	else
		select "no change";
		set ret = 0;
	end if;
END

$$

CREATE PROCEDURE `check_suspended` (sysid varchar(40), OUT ret int)
BEGIN
	declare date_1_days date;
	declare date_90_days date;
	declare ammonium_num int;
	declare nitrite_num int;
	declare nitrate_num int;
	set date_90_days = (select DATE_SUB(CURDATE(), INTERVAL 90 DAY) as date from dual);
	set date_1_days = (select DATE_SUB(CURDATE(), INTERVAL 1 DAY) as date from dual);
	/*check ammonium values*/
	call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_1_days, ammonium_num);
	/*check nitrate values*/
	call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_1_days, nitrate_num);
	/*check nitrite values*/
	call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_1_days, nitrite_num);
	if ammonium_num >= 1 and nitrate_num >= 1 and nitrite_num >= 1 then
		select "change to pre-Established";
		set ret = 1;
	else
		select "no change";
		set ret = 0;
	end if;
	/*check ammonium values*/
	call get_measurement_count(CONCAT('aqxs_ammonium_',sysid), date_90_days, ammonium_num);
	/*check nitrate values*/
	call get_measurement_count(CONCAT('aqxs_nitrate_',sysid), date_90_days, nitrate_num);
	/*check nitrite values*/
	call get_measurement_count(CONCAT('aqxs_nitrite_',sysid), date_90_days, nitrite_num);
	if ammonium_num < 1 and nitrate_num < 1 and nitrite_num < 1 then
		select "change to terminated";
		set ret = 2;
	else
		select "no change";
		set ret = 0;
	end if;

	/*logic to check for remove_plant and remove_fish, if yes set ret to 2*/
END

$$

CREATE PROCEDURE `compare_readings` (sysid varchar(40), OUT ret int)
BEGIN

	declare num1 int;
	declare num2 int;

	set @GetSystem = concat('select count(*) from
	(select value,@curRow := @curRow - 1 AS rown
	 from aqxs_ammonium_',sysid,' a
	JOIN    (SELECT @curRow := 7) r
	order by a.time desc limit 7) ammonium,
	(select value,@curRow1 := @curRow1 - 1 AS rown
	 from aqxs_nitrate_',sysid,' a
	JOIN    (SELECT @curRow1 := 7) r
	order by a.time desc limit 7) nitrate
	where ammonium.value > nitrate.value
	and ammonium.rown = nitrate.rown into @num1');
	prepare stmt from @GetSystem;
	execute stmt;
	set num1 = @num1;
	set @GetSystem = concat('select count(*) from
	(select value,@curRow := @curRow - 1 AS rown
	 from aqxs_nitrite_',sysid,' a
	JOIN    (SELECT @curRow := 7) r
	order by a.time desc limit 7) ammonium,
	(select value,@curRow1 := @curRow1 - 1 AS rown
	 from aqxs_nitrate_',sysid,' a
	JOIN    (SELECT @curRow1 := 7) r
	order by a.time desc limit 7) nitrate
	where ammonium.value > nitrate.value
	and ammonium.rown = nitrate.rown into @num2');
	prepare stmt from @GetSystem;
	execute stmt;
	set num2 = @num2;
	if num1 = 7 and num2 = 7 then
		/*change to pre-established*/
		set ret = 1;
	else
		set ret = 0;
	end if;

END