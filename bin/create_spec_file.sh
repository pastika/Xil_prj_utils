echo "Creation du fichier spec..."

name_paquet=$1
DIR_TO_INSTALL=$4

#Sanitize inputs based on https://stackoverflow.com/a/94500/665025
# replace / with _
THREE=${3////_}
# replace spaces with _
THREE=${THREE// /_}
# clean out anything that's not alphanumeric or an underscore
THREE=${THREE//[^a-zA-Z0-9_]/}

#Same for $2
# replace / with _
TWO=${2////_}
# replace spaces with _
TWO=${TWO// /_}
# clean out anything that's not alphanumeric or an underscore
TWO=${TWO//[^a-zA-Z0-9_]/}


SPEC_FILE="${HOME}/rpmbuild/SPECS/${name_paquet}-${TWO}-${THREE}.spec"

Big=0
if [ $# -ge 5 ]
then
	Big=1
fi



## écriture dans SPEC_FILE
> $SPEC_FILE
echo -e "Name:     ${name_paquet}" > $SPEC_FILE
echo -e "Version:  ${TWO}" >> $SPEC_FILE
echo -e "Release:  ${THREE}" >> $SPEC_FILE
echo -e "Summary:        Install the ${name_paquet} arborescence files on your system in $DIR_TO_INSTALL" >> $SPEC_FILE
echo -e "URL: ${CI_PROJECT_URL} \n " >> $SPEC_FILE

shift
shift
shift
shift

#echo -e "Group: Sciences/Mathematics" >> $SPEC_FILE
echo -e "License:        CERN" >> $SPEC_FILE


if [ $Big == 1 ]
then
	echo -e "Requires: $@ " >> $SPEC_FILE
fi

echo -e "BuildRoot: %{_topdir}/BUILDROOT/" >> $SPEC_FILE

echo -e "%prep" >> $SPEC_FILE


echo -e "%description" >> $SPEC_FILE
echo -e "It's a package which install arborescence files of ${name_paquet} in $DIR_TO_INSTALL on your system \n " >> $SPEC_FILE

echo -e "%build" >> $SPEC_FILE

echo -e "%install" >> $SPEC_FILE
if [ $Big == 0 ]
then
	echo -e 'rm -rf $RPM_BUILD_ROOT;' >> $SPEC_FILE
	echo -e "mkdir -p \$RPM_BUILD_ROOT$DIR_TO_INSTALL" >> $SPEC_FILE 
	echo -e "cd %{_sourcedir}" >> $SPEC_FILE
	echo -e "mv $name_paquet \$RPM_BUILD_ROOT$DIR_TO_INSTALL" >> $SPEC_FILE 

	echo -e "%files" >> $SPEC_FILE
	echo -e "%defattr(-,root,root)"  >> $SPEC_FILE
	echo -e "$DIR_TO_INSTALL/$name_paquet" >> $SPEC_FILE 
else
	echo -e "%files" >> $SPEC_FILE
fi


##retour au script
echo "cat SPEC_FILE=${SPEC_FILE}"
cat $SPEC_FILE
