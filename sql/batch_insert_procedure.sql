-- 存储过程批量添加测试数据
delimiter ;;

create  procedure `batchInsert` (in start_num int, in max_num int)
begin
	declare i int default start_num;
	while i < max_num do
		insert into `order`(id,score,name) values (i, rand()*10000000,concat('user_',i));
		set i = i+1;
	end while;
end

delimiter ;;

show procedure status;

call batchInsert (1, 1000000);



-- 优化改进版本
delimiter ;;

create procedure `batchInsert02` (in sta_num int, in max_num int)
begin
	declare i int default sta_num;
	set @pre_sql = 'insert into `order` (id,score,name) values ';
	set @excute_sql = @pre_sql;

	-- 循环

	while i < max_num do
		set @excute_sql = concat(@excute_sql, '(', i ,',', rand()*1000000,',',concat('buser_',i),'),') ;
		set i = i+1;
		if i mod 1000 = 0 or i>= max_num then
			set @excute_sql = substring(@excute_sql, 1, char_length(@excute_sql)-1);
			prepare stmt from @excute_sql;
			execute stmt;
			deallocate prepare stmt;
			if i< max_num then
				set @excute_sql = @pre_sql;
			end if;
		end if;
	end while;
end

delimiter;;
call batchInsert02 (1000000, 2000000);


--
create table `order`(
`id` int(11) unsigned not null auto_increment,
`score` int(11) not null,
`name` varchar(11) not null default '',
primary key(`id`)
) engine = InnoDB auto_increment=100000 default charset = utf8mb4;
