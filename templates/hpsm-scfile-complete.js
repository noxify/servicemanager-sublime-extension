var f${0:File} = new SCFile( "${1:tablename}" );
var q${0:File} = true; 
var rc${0:File} = f${0:File}.doSelect( q${0:File} );

while( rc${0:File} == RC_SUCCESS ) {
	//your code 
	rc${0:File} = f${0:File}.getNext();
}